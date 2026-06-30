"""
ProcessMonitor: manages local traffic algorithm subprocesses.

Singleton service used by the deployments API to start/stop traffic modules
as backend-embedded subprocesses and to reconcile zombie deployments on
startup.
"""

import asyncio
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional, Set

try:
    import pynvml

    _PYNVML_AVAILABLE = True
except Exception:
    pynvml = None  # type: ignore
    _PYNVML_AVAILABLE = False

import yaml
from sqlalchemy import update

from app.models.deployment import Deployment


# Modules that may be spawned as local traffic algorithm subprocesses.
TRAFFIC_MODULE_WHITELIST = {
    "traffic_jam",
    "vehicle_counting",
    "reverse_detection",
    "pedestrian_intrusion",
    "accident_detection",
    "vest_detection",
}

# Workspace root that contains both `ai-console` and `traffic` directories.
_PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Default machine-to-machine ingest endpoint used by traffic modules.
_DEFAULT_INGEST_ENDPOINT = "http://127.0.0.1:10088/api/v1/algorithm-events/ingest"

# Token length generated for each deployment (URL-safe base64 ~64 chars).
_TOKEN_NBYTES = 48

# Default restart policy.
_DEFAULT_RESTART_POLICY = {"delay": 5, "max_retries": 3}

# Watchdog check interval in seconds.
_WATCHDOG_INTERVAL = 5

# Minimum free GPU memory (MB) required to start a process.
# Each traffic module loads YOLO main model (~1.0GB) + pedestrian detector
# (~1.0GB) + reverse-detect/vest models (~0.5GB) + inference batch buffers
# (~0.3GB). Empirically ~2.5GB+ per process. Raised from 1536 to 3072 to
# reject a start that would immediately OOM rather than letting the watchdog
# restart it on a tight GPU.
_MIN_GPU_MEMORY_MB = 3072

# Stagger delay (seconds) inserted before asyncio.create_subprocess_exec.
# 30 deployments × 6 algorithms used to fork simultaneously and fight for the
# same 24GB GPU. A 3-second serial offset per start() gives each subprocess
# time to load its model and pin VRAM before the next one starts.
_STARTUP_STAGGER_SECONDS = 3

# Hard cap on concurrently-running traffic subprocesses per backend process.
# When the count is already at the cap, additional start() calls block
# (asyncio.sleep polling) until an existing subprocess exits. This stops
# the 30-process startup burst that exhausted GPU memory.
_MAX_CONCURRENT_DEPLOYMENTS = 8

# Per-GPU cap. The effective cap is scaled by the number of available GPUs
# so that adding more cards allows more concurrent inferences without
# overloading any single GPU.
_MAX_CONCURRENT_DEPLOYMENTS_PER_GPU = 9

# Poll interval (seconds) for waiting on a free concurrency slot.
_CONCURRENCY_POLL_INTERVAL = 2


# Whether NVML has been initialized in this process.
_NVML_INITIALIZED = False


def _nvml_init_once() -> None:
    """Initialize NVML once per process."""
    global _NVML_INITIALIZED
    if not _NVML_INITIALIZED and pynvml is not None:
        pynvml.nvmlInit()
        _NVML_INITIALIZED = True


class ProcessMonitor:
    """
    Singleton process monitor for traffic algorithm subprocesses.

    Tracks in-flight processes by Deployment.id and handles lifecycle,
    token generation, temporary configuration, startup reconciliation,
    automatic restart with retry limits, and GPU pre-flight checks.
    """

    _instance: Optional["ProcessMonitor"] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _gpu_lock: asyncio.Lock = asyncio.Lock()
    _next_gpu_index: int = 0

    @classmethod
    def generate_token(cls) -> str:
        """Generate a new deployment token."""
        return secrets.token_urlsafe(_TOKEN_NBYTES)

    def __new__(cls) -> "ProcessMonitor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ingest_endpoint: Optional[str] = None) -> None:
        if self._initialized:
            return
        self._initialized = True

        self.ingest_endpoint = ingest_endpoint or _DEFAULT_INGEST_ENDPOINT
        # deployment_id -> process metadata
        self._processes: Dict[int, Dict[str, Any]] = {}
        # deployment_ids that were intentionally stopped by user/API
        self._intentional_stops: Set[int] = set()
        # deployment_id -> number of restart attempts
        self._restart_counts: Dict[int, int] = {}
        # number of start() calls currently past the GPU check and waiting to
        # fork (or just past the fork). Counted by the concurrency gate to
        # avoid the TOCTOU race where N callers all see alive_count=7 and
        # all proceed. Decremented in a try/finally in start().
        self._in_flight_starts: int = 0
        # timestamp of the last reconcile() call
        self._reconcile_timestamp: float = 0.0
        # registered async callback for DB status updates
        # Signature: async def callback(deployment_id, status, pid, token=None)
        # `token` is forwarded only when the monitor rotated it (e.g. watchdog restart).
        self._status_callback: Optional[
            Callable[[int, str, Optional[int], Optional[str]], Awaitable[None]]
        ] = None
        # background watchdog task
        self._watchdog_task: Optional[asyncio.Task] = None

    def register_status_callback(
        self,
        callback: Callable[[int, str, Optional[int], Optional[str]], Awaitable[None]],
    ) -> None:
        """Register an async callback to update deployment status in the DB.

        Signature: async def callback(deployment_id: int, status: str, pid: Optional[int], token: Optional[str] = None)
        `token` is forwarded when the monitor rotated the deployment token.
        """
        self._status_callback = callback

    @staticmethod
    def _is_stream_url(url: str) -> bool:
        """Return True for RTSP / RTMP / HTTP(S) stream URLs."""
        return url.startswith(("rtsp://", "rtmp://", "http://", "https://"))

    @staticmethod
    def _available_gpu_ids() -> list[int]:
        """Return list of GPU indices reported by NVML / nvidia-smi."""
        if _PYNVML_AVAILABLE:
            try:
                _nvml_init_once()
                return list(range(pynvml.nvmlDeviceGetCount()))
            except Exception:
                pass
        return ProcessMonitor._available_gpu_ids_via_smi()

    @staticmethod
    def _available_gpu_ids_via_smi() -> list[int]:
        """Fallback GPU enumeration using nvidia-smi."""
        if not shutil.which("nvidia-smi"):
            return []
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=index",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return []
            return [int(line.strip()) for line in result.stdout.strip().splitlines() if line.strip()]
        except Exception:
            return []

    @staticmethod
    def _gpu_memory_free(gpu_id: int = 0) -> Optional[float]:
        """Query free memory (MB) on the specified GPU via NVML / nvidia-smi."""
        if _PYNVML_AVAILABLE:
            try:
                _nvml_init_once()
                handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                return float(info.free) / (1024 * 1024)
            except Exception:
                pass
        return ProcessMonitor._gpu_memory_free_via_smi(gpu_id)

    @staticmethod
    def _gpu_memory_free_via_smi(gpu_id: int = 0) -> Optional[float]:
        """Fallback free-memory query using nvidia-smi."""
        if not shutil.which("nvidia-smi"):
            return None
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.free",
                    "--format=csv,noheader,nounits",
                    f"--id={gpu_id}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None
            return float(result.stdout.strip().splitlines()[0].strip())
        except Exception:
            return None

    @classmethod
    async def _select_gpu(cls, gpu_ids: list[int]) -> Optional[int]:
        """Pick a GPU in round-robin order that meets the minimum memory requirement."""
        if not gpu_ids:
            return None
        async with cls._gpu_lock:
            offset = cls._next_gpu_index % len(gpu_ids)
            for i in range(len(gpu_ids)):
                gpu_id = gpu_ids[(offset + i) % len(gpu_ids)]
                free_mb = cls._gpu_memory_free(gpu_id)
                if free_mb is not None and free_mb >= _MIN_GPU_MEMORY_MB:
                    cls._next_gpu_index = (offset + i + 1) % len(gpu_ids)
                    return gpu_id
            return None

    def start_watchdog(self) -> None:
        """Start the background watchdog task if not already running."""
        if self._watchdog_task is None or self._watchdog_task.done():
            self._watchdog_task = asyncio.create_task(self._watchdog_loop())

    async def stop_watchdog(self) -> None:
        """Stop the background watchdog task."""
        if self._watchdog_task and not self._watchdog_task.done():
            self._watchdog_task.cancel()
            try:
                await self._watchdog_task
            except asyncio.CancelledError:
                pass
            self._watchdog_task = None

    def _load_module_config(
        self,
        module_name: str,
        user_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Load base.yaml + module config.yaml and merge with user_config."""
        base_path = _PROJECT_ROOT / "traffic" / "config" / "base.yaml"
        module_path = (
            _PROJECT_ROOT / "traffic" / "modules" / module_name / "config" / "config.yaml"
        )

        merged: Dict[str, Any] = {}
        for path in (base_path, module_path):
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    merged = self._deep_merge(merged, data)
                except (OSError, yaml.YAMLError):
                    pass

        return self._deep_merge(merged, user_config)

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge override into base."""
        result = dict(base)
        for key, val in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(val, dict)
            ):
                result[key] = ProcessMonitor._deep_merge(result[key], val)
            else:
                result[key] = val
        return result

    async def start(
        self,
        module_name: str,
        video_path: str,
        deployment_id: int,
        stream_id: str,
        config: Optional[Dict[str, Any]] = None,
        log_path: Optional[str] = None,
        restart_policy: Optional[Dict[str, Any]] = None,
        deployment_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start a traffic module subprocess.

        Returns {"deployment_token": str, "pid": int, "log_path": str|None}.
        """
        if module_name not in TRAFFIC_MODULE_WHITELIST:
            raise ValueError(f"Module '{module_name}' is not in the allowed whitelist")

        if not video_path or ".." in video_path:
            raise ValueError("video_path must not be empty and must not contain path traversal")

        if not stream_id:
            raise ValueError("stream_id must not be empty")
        stream_id = str(stream_id)

        is_stream = self._is_stream_url(video_path)
        if not is_stream:
            if video_path.startswith("docs/"):
                video_path = str((_PROJECT_ROOT / video_path).resolve())
            elif not os.path.isabs(video_path):
                raise ValueError("video_path must be absolute for local files")

        if not is_stream:
            video_file = Path(video_path)
            if not video_file.is_file():
                raise ValueError(f"video_path does not exist or is not a file: {video_path}")

        # GPU pre-flight check: pick the GPU with the most free memory and
        # restrict the subprocess to that card via CUDA_VISIBLE_DEVICES.
        gpu_ids = self._available_gpu_ids()
        selected_gpu: Optional[int] = None
        if gpu_ids:
            selected_gpu = await self._select_gpu(gpu_ids)
            if selected_gpu is None:
                raise RuntimeError(
                    f"No GPU has sufficient memory: required {_MIN_GPU_MEMORY_MB} MB"
                )
        else:
            import logging

            logging.warning("nvidia-smi unavailable, skipping GPU memory pre-flight check")

        # Concurrency cap scales with the number of GPUs so that adding cards
        # increases total throughput without overloading any single GPU.
        max_concurrent = max(
            _MAX_CONCURRENT_DEPLOYMENTS,
            len(gpu_ids) * _MAX_CONCURRENT_DEPLOYMENTS_PER_GPU,
        )

        policy = {**_DEFAULT_RESTART_POLICY, **(restart_policy or {})}

        # Concurrency cap: count both already-alive subprocesses AND other
        # start() calls currently between the gate and the fork, so a burst
        # of 30 simultaneous start() calls cannot overshoot the cap. We
        # increment _in_flight_starts as soon as we decide to proceed and
        # decrement it in the finally below (success or failure).
        import logging

        while True:
            alive_count = sum(
                1
                for meta in self._processes.values()
                if meta["process"].returncode is None
                and self._is_pid_alive(meta["process"].pid)
            )
            if alive_count + self._in_flight_starts < max_concurrent:
                break
            logging.info(
                "Concurrency cap reached (alive=%d + in_flight=%d / cap=%d); waiting %ds for free slot before starting deployment %d",
                alive_count,
                self._in_flight_starts,
                max_concurrent,
                _CONCURRENCY_POLL_INTERVAL,
                deployment_id,
            )
            await asyncio.sleep(_CONCURRENCY_POLL_INTERVAL)

        # Reserve a slot for THIS start() so concurrent callers see the
        # incremented counter and wait. Released in finally below.
        self._in_flight_starts += 1

        # Stagger only when there are already-alive subprocesses fighting
        # for the GPU. Solo starts (e.g. recovery after a single crash)
        # don't need the delay.
        if alive_count > 0:
            logging.info(
                "Staggering startup of deployment %d by %ds (alive=%d)",
                deployment_id,
                _STARTUP_STAGGER_SECONDS,
                alive_count,
            )
            await asyncio.sleep(_STARTUP_STAGGER_SECONDS)

        # From this point until the slot is released below, _in_flight_starts
        # is bumped. Release it on every exit path (success, exception) so
        # the next start() caller can take our slot.
        try:
            async with self._lock:
                if deployment_id in self._processes:
                    raise RuntimeError(f"Deployment {deployment_id} already has a running process")

                token = deployment_token or secrets.token_urlsafe(_TOKEN_NBYTES)
                full_config = self._load_module_config(module_name, config or {})
                tmp_config_path = self._write_config(full_config, token)

                stdout_target = asyncio.subprocess.DEVNULL
                stderr_target = asyncio.subprocess.DEVNULL
                log_file_handle = None
                if log_path:
                    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
                    log_file_handle = open(log_path, "ab")
                    stdout_target = log_file_handle
                    stderr_target = log_file_handle

                env = os.environ.copy()
                if selected_gpu is not None:
                    env["CUDA_VISIBLE_DEVICES"] = str(selected_gpu)
                traffic_common = str(_PROJECT_ROOT / "traffic" / "common")
                existing_pp = env.get("PYTHONPATH", "")
                env["PYTHONPATH"] = (
                    f"{traffic_common}{os.pathsep}{existing_pp}" if existing_pp else traffic_common
                )

                try:
                    process = await asyncio.create_subprocess_exec(
                        sys.executable,
                        "-m",
                        f"traffic.modules.{module_name}.main",
                        "--config",
                        str(tmp_config_path),
                        "--source",
                        video_path if is_stream else str(video_file.resolve()),
                        "--stream-id",
                        stream_id,
                        cwd=str(_PROJECT_ROOT),
                        stdout=stdout_target,
                        stderr=stderr_target,
                        env=env,
                    )
                except (OSError, asyncio.CancelledError):
                    if log_file_handle:
                        log_file_handle.close()
                    self._safe_remove(tmp_config_path)
                    raise

                self._processes[deployment_id] = {
                    "process": process,
                    "module_name": module_name,
                    "video_path": video_path if is_stream else str(video_file.resolve()),
                    "stream_id": stream_id,
                    "user_config": dict(config) if config else {},
                    "config_path": tmp_config_path,
                    "deployment_token": token,
                    "log_path": log_path,
                    "log_file_handle": log_file_handle,
                    "restart_policy": policy,
                    "started_at": time.monotonic(),
                }
                # Clear any stale intentional-stop / restart-count state
                self._intentional_stops.discard(deployment_id)
                self._restart_counts.pop(deployment_id, None)

                # Ensure watchdog is running
                if self._watchdog_task is None or self._watchdog_task.done():
                    self._watchdog_task = asyncio.create_task(self._watchdog_loop())

                return {
                    "deployment_token": token,
                    "pid": process.pid,
                    "log_path": log_path,
                }
        finally:
            self._in_flight_starts = max(0, self._in_flight_starts - 1)

    async def stop(self, deployment_id: int) -> Dict[str, Any]:
        """
        Stop a traffic module subprocess.

        Returns {"pid": int|None, "exit_code": int|None}.
        """
        async with self._lock:
            self._intentional_stops.add(deployment_id)
            self._restart_counts.pop(deployment_id, None)

            meta = self._processes.pop(deployment_id, None)
            if meta is None:
                return {"pid": None, "exit_code": None}

            process: asyncio.subprocess.Process = meta["process"]
            config_path: Path = meta["config_path"]
            log_file_handle = meta.get("log_file_handle")

            try:
                if process.returncode is None:
                    try:
                        process.send_signal(signal.SIGTERM)
                    except ProcessLookupError:
                        pass

                    try:
                        await asyncio.wait_for(process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                        await process.wait()
            finally:
                if log_file_handle:
                    log_file_handle.close()
                self._safe_remove(config_path)

            # Verify PID is gone
            if self._is_pid_alive(process.pid):
                import logging

                logging.warning("Process %s still alive after stop for deployment %s", process.pid, deployment_id)

            return {"pid": process.pid, "exit_code": process.returncode}

    async def _watchdog_loop(self) -> None:
        """Background task that checks tracked processes and restarts crashed ones."""
        import logging

        while True:
            try:
                await asyncio.sleep(_WATCHDOG_INTERVAL)
            except asyncio.CancelledError:
                break

            async with self._lock:
                # Only manage processes started after the last reconcile
                cutoff = self._reconcile_timestamp
                items = list(self._processes.items())

            for deployment_id, meta in items:
                started_at = meta.get("started_at", 0.0)
                if started_at <= cutoff:
                    continue

                process: asyncio.subprocess.Process = meta["process"]
                if process.returncode is None and self._is_pid_alive(process.pid):
                    continue

                # Process died
                async with self._lock:
                    if deployment_id in self._intentional_stops:
                        self._intentional_stops.discard(deployment_id)
                        self._processes.pop(deployment_id, None)
                        self._restart_counts.pop(deployment_id, None)
                        if self._status_callback:
                            try:
                                await self._status_callback(deployment_id, "stopped", None)
                            except Exception:
                                logging.exception("Status callback failed for deployment %s", deployment_id)
                        continue

                    # Normal completion (exit code 0): traffic module finished
                    # reading the input video and returned cleanly. This is NOT
                    # a crash and should NOT be restarted automatically. Mark
                    # as 'completed' and forget the deployment so the next
                    # reconcile() / restart() can pick it up explicitly.
                    if process.returncode == 0:
                        self._processes.pop(deployment_id, None)
                        self._restart_counts.pop(deployment_id, None)
                        if self._status_callback:
                            try:
                                await self._status_callback(deployment_id, "completed", None)
                            except Exception:
                                logging.exception("Status callback failed for deployment %s", deployment_id)
                        logging.info(
                            "Deployment %d completed normally (exit_code=0); not restarting",
                            deployment_id,
                        )
                        continue

                    policy = meta.get("restart_policy", _DEFAULT_RESTART_POLICY)
                    max_retries = int(policy.get("max_retries", 3))
                    delay = float(policy.get("delay", 5))

                    restarts = self._restart_counts.get(deployment_id, 0)
                    if restarts >= max_retries:
                        self._processes.pop(deployment_id, None)
                        self._restart_counts.pop(deployment_id, None)
                        if self._status_callback:
                            try:
                                await self._status_callback(deployment_id, "error", None)
                            except Exception:
                                logging.exception("Status callback failed for deployment %s", deployment_id)
                        continue

                    self._restart_counts[deployment_id] = restarts + 1
                    # Remove stale metadata so start() can recreate the deployment.
                    old_meta = self._processes.pop(deployment_id, None)
                    if old_meta:
                        old_log_handle = old_meta.get("log_file_handle")
                        if old_log_handle:
                            old_log_handle.close()
                        self._safe_remove(old_meta.get("config_path"))

                # Restart outside the lock to avoid blocking other ops
                await asyncio.sleep(delay)

                try:
                    # Generate and persist the new token before forking so the
                    # ingest endpoint can authenticate the restarted process
                    # from its first frame.
                    new_token = self.generate_token()
                    if self._status_callback:
                        try:
                            await self._status_callback(
                                deployment_id, "running", None, new_token
                            )
                        except Exception:
                            logging.exception("Status callback failed for deployment %s", deployment_id)

                    result = await self.start(
                        module_name=meta["module_name"],
                        video_path=meta["video_path"],
                        deployment_id=deployment_id,
                        stream_id=meta["stream_id"],
                        config=meta.get("user_config"),
                        log_path=meta.get("log_path"),
                        restart_policy=policy,
                        deployment_token=new_token,
                    )
                    if self._status_callback:
                        try:
                            await self._status_callback(
                                deployment_id, "running", result.get("pid"), new_token
                            )
                        except Exception:
                            logging.exception("Status callback failed for deployment %s", deployment_id)
                except Exception as exc:
                    logging.exception("Failed to restart deployment %s: %s", deployment_id, exc)
                    async with self._lock:
                        self._processes.pop(deployment_id, None)
                        self._restart_counts.pop(deployment_id, None)
                    if self._status_callback:
                        try:
                            await self._status_callback(deployment_id, "error", None)
                        except Exception:
                            logging.exception("Status callback failed for deployment %s", deployment_id)

    async def reconcile(self, db: Any) -> None:
        """
        Mark all deployments that look running but have no live process as
        crashed, clear the in-memory process map, and record reconcile timestamp.

        `db` must be an async SQLAlchemy session.

        PID-liveness check: a previous backend's traffic subprocesses are
        detached children that survive a backend restart. If we blanket-mark
        every "running" deployment as crashed, those still-alive subprocesses
        will keep pushing events to /api/v1/algorithm-events/ingest and hit
        the "Deployment is not running" 403 because the DB now says crashed.
        We therefore probe each deployment's stored pid with os.kill(pid, 0)
        and only mark deployments whose pid is actually gone.
        """
        import logging
        import time

        async with self._lock:
            # Look up every deployment that was marked "running" by a prior
            # backend, plus its stored pid. We can't rely on the in-memory
            # _processes map because reconcile runs before the monitor ever
            # tracks anything in this process.
            from sqlalchemy import select

            rows = (await db.execute(
                select(Deployment.id, Deployment.pid)
                .where(Deployment.algorithm_status == "running")
            )).all()

            crashed_ids = []
            for deployment_id, pid in rows:
                if pid is None or not self._is_pid_alive(pid):
                    crashed_ids.append(deployment_id)

            if crashed_ids:
                try:
                    await db.execute(
                        update(Deployment)
                        .where(Deployment.id.in_(crashed_ids))
                        .values(algorithm_status="crashed", stopped_at=None)
                    )
                    await db.commit()
                except Exception:
                    # A transient DB hiccup at backend startup must not
                    # cascade into the running backend. Roll back, log, and
                    # continue so the in-memory map still gets cleared below.
                    try:
                        await db.rollback()
                    except Exception:
                        logging.exception("reconcile: rollback failed")
                    logging.exception(
                        "reconcile: failed to mark %d deployments as crashed",
                        len(crashed_ids),
                    )
                else:
                    logging.info(
                        "reconcile: marked %d zombie deployments as crashed (alive pids kept running): %s",
                        len(crashed_ids),
                        crashed_ids,
                    )
            else:
                # No-op: don't issue an UPDATE if every recorded pid is still alive.
                logging.info(
                    "reconcile: 0 zombies to mark crashed (%d 'running' deployments, all pids alive)",
                    len(rows),
                )

            # Any still-tracked processes are orphaned by the previous backend
            # process; clear the map without touching the OS processes.
            for meta in self._processes.values():
                log_file_handle = meta.get("log_file_handle")
                if log_file_handle:
                    log_file_handle.close()
                self._safe_remove(meta["config_path"])
            self._processes.clear()
            self._intentional_stops.clear()
            self._restart_counts.clear()
            self._reconcile_timestamp = time.monotonic()

    def is_deployment_running(self, deployment_id: int) -> bool:
        """Return True if the deployment has a tracked, alive subprocess."""
        meta = self._processes.get(deployment_id)
        if meta is None:
            return False
        process = meta["process"]
        if process.returncode is not None:
            return False
        return self._is_pid_alive(process.pid)

    def is_process_running(self, deployment_id: int) -> bool:
        """Public helper: return True if deployment process is tracked and alive."""
        return self.is_deployment_running(deployment_id)

    def get_pid(self, deployment_id: int) -> Optional[int]:
        meta = self._processes.get(deployment_id)
        if meta is None:
            return None
        return meta["process"].pid

    def get_exit_code(self, deployment_id: int) -> Optional[int]:
        meta = self._processes.get(deployment_id)
        if meta is None:
            return None
        return meta["process"].returncode

    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        """Return True if process `pid` exists."""
        try:
            os.kill(pid, 0)
        except (OSError, ProcessLookupError):
            return False
        return True

    def _write_config(self, user_config: Dict[str, Any], token: str) -> Path:
        """Merge runtime HTTP config with user config and write to a temp file."""
        runtime_dir = _PROJECT_ROOT / "traffic" / ".runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)

        runtime_http = {
            "endpoint": self.ingest_endpoint,
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        }
        merged_config = dict(user_config)
        existing_http = merged_config.get("http", {})
        merged_http = {**existing_http, **runtime_http}
        existing_headers = existing_http.get("headers", {})
        merged_http["headers"] = {**existing_headers, **runtime_http["headers"]}
        merged_config["http"] = merged_http

        fd, path = tempfile.mkstemp(
            suffix=".yaml",
            prefix="traffic_config_",
            dir=str(_PROJECT_ROOT / "traffic" / ".runtime"),
        )
        fd_opened = False
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                fd_opened = True
                yaml.safe_dump(merged_config, f, default_flow_style=False, sort_keys=False)
        except (OSError, yaml.YAMLError):
            if not fd_opened:
                os.close(fd)
            self._safe_remove(Path(path))
            raise

        return Path(path)

    @staticmethod
    def _safe_remove(path: Optional[Path]) -> None:
        if path is None:
            return
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
