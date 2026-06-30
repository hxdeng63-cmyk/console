import asyncio
import logging
import time
import uuid
from typing import Any, Awaitable, Callable, Optional


class AsyncTaskManager:
    """Generic in-memory store for fire-and-forget background tasks.

    Mirrors the semantics used by ``restart-all`` so that long-running
    endpoints can return a ``task_id`` immediately and let the caller poll
    ``/.../status/{task_id}`` for progress.
    """

    def __init__(self, completed_task_ttl_seconds: float = 3600.0) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._completed_task_ttl_seconds = completed_task_ttl_seconds

    def create_task(
        self,
        status: str = "pending",
        extra: Optional[dict[str, Any]] = None,
    ) -> str:
        """Create a pending task and return its id."""
        task_id = str(uuid.uuid4())
        task: dict[str, Any] = {
            "status": status,
            "total": 0,
            "done": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "error": None,
            "completed_at": None,
        }
        if extra:
            task.update(extra)
        self._tasks[task_id] = task
        self._prune_completed_tasks()
        return task_id

    async def get_task(self, task_id: str) -> Optional[dict[str, Any]]:
        """Return a lock-protected shallow copy of the task state."""
        async with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task else None

    async def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        """Atomically update a task's state."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            if status is not None:
                task["status"] = status
            if extra:
                task.update(extra)
            if status in ("completed", "failed"):
                task["completed_at"] = time.monotonic()

    def run_task(
        self,
        task_id: str,
        coro_func: Callable[[str], Awaitable[Any]],
    ) -> None:
        """Schedule ``coro_func(task_id)`` as a background task.

        The coroutine is responsible for calling ``update_task`` to publish
        progress. Exceptions are caught and recorded as ``failed``.
        """
        asyncio.create_task(self._background_runner(task_id, coro_func))

    async def _background_runner(
        self,
        task_id: str,
        coro_func: Callable[[str], Awaitable[Any]],
    ) -> None:
        try:
            await coro_func(task_id)
        except Exception as exc:
            logging.exception("Background task %s failed", task_id)
            await self.update_task(task_id, "failed", {"error": str(exc)})

    def _prune_completed_tasks(self) -> None:
        """Remove old terminal tasks to keep the store bounded."""
        now = time.monotonic()
        stale_keys = [
            task_id
            for task_id, info in list(self._tasks.items())
            if info.get("status") in ("completed", "failed")
            and now - (info.get("completed_at") or now) > self._completed_task_ttl_seconds
        ]
        for task_id in stale_keys:
            del self._tasks[task_id]


# Module-level singleton for use across endpoints.
async_task_manager = AsyncTaskManager()
