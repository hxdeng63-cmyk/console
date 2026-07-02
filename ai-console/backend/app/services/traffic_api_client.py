"""traffic-api 客户端：纯 async 转发层。

`traffic-api` 是外部纯推理服务（不持久化，重启后状态丢失），本客户端只负责：
  1. HTTP 调用（httpx.AsyncClient）
  2. 鉴权头注入（Authorization: Bearer <TRAFFIC_API_AUTH_TOKEN>）
  3. 错误分类（6 类业务异常）

设计原则：
  - 不持有任何状态（无全局可变对象）；每次调用新建 client 或复用调用方传入的 client
  - 不在内部 catch 业务异常（让上层决定如何响应）
  - 错误码映射严格对齐 API_SERVICE(1).md

错误映射：
  401 → TrafficApiAuthError        → 我们的后端 HTTP 502
  404 → TrafficApiNotFoundError     → 我们的后端 HTTP 404
  409 → TrafficApiConflictError     → 我们的后端 HTTP 409
  503 → TrafficApiResourceError     → 我们的后端 HTTP 503
  5xx → TrafficApiServerError       → 我们的后端 HTTP 502
  连接错误/超时 → TrafficApiUnavailableError → 我们的后端 HTTP 503
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


# ---- 错误层级（6 类） -----------------------------------------------

class TrafficApiError(Exception):
    """traffic-api 调用错误基类。"""

    def __init__(self, message: str, *, status_code: int = 502, payload: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class TrafficApiAuthError(TrafficApiError):
    """401 — 鉴权失败。"""


class TrafficApiNotFoundError(TrafficApiError):
    """404 — 资源不存在（status 查询时也用于表示 traffic-api 重启后任务记录丢失）。"""


class TrafficApiConflictError(TrafficApiError):
    """409 — 状态冲突（如重复 start 同一 deployment）。"""


class TrafficApiResourceError(TrafficApiError):
    """503 — 资源不足（GPU 显存、并发数超限）。"""


class TrafficApiServerError(TrafficApiError):
    """5xx — traffic-api 内部错误。"""


class TrafficApiUnavailableError(TrafficApiError):
    """连接错误 / 超时 — traffic-api 不可达。"""


# ---- 客户端 -------------------------------------------------------

class TrafficApiClient:
    """traffic-api 异步 HTTP 客户端。"""

    def __init__(self, *, base_url: Optional[str] = None, auth_token: Optional[str] = None,
                 timeout: Optional[float] = None) -> None:
        self._base_url = (base_url or settings.TRAFFIC_API_BASE_URL).rstrip("/")
        self._auth_token = auth_token or settings.TRAFFIC_API_AUTH_TOKEN
        self._timeout = timeout if timeout is not None else settings.TRAFFIC_API_REQUEST_TIMEOUT

    # ---- 内部辅助 ------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._auth_token}"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """统一 HTTP 调用 + 错误映射。返回 traffic-api 响应的 `data` 字段或 None。"""
        url = f"{self._base_url}{path}"
        headers = kwargs.pop("headers", {}) or {}
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Authorization", f"Bearer {self._auth_token}")
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.request(method, url, headers=headers, **kwargs)
        except httpx.TimeoutException as exc:
            raise TrafficApiUnavailableError(
                f"traffic-api 超时: {method} {path}", status_code=503
            ) from exc
        except httpx.ConnectError as exc:
            raise TrafficApiUnavailableError(
                f"traffic-api 不可达: {method} {path} — {exc}", status_code=503
            ) from exc
        except httpx.HTTPError as exc:
            raise TrafficApiUnavailableError(
                f"traffic-api 网络错误: {method} {path} — {exc}", status_code=503
            ) from exc

        return self._parse(resp, method, path)

    @staticmethod
    def _parse(resp: httpx.Response, method: str, path: str) -> Any:
        """解析 traffic-api 响应，映射错误码。"""
        if resp.status_code == 200 or resp.status_code == 201:
            try:
                body = resp.json()
            except ValueError:
                return resp.text
            # traffic-api 统一响应格式：{"code": 200, "message": "ok", "data": ...}
            if isinstance(body, dict) and "data" in body:
                return body.get("data")
            return body
        if resp.status_code == 401:
            raise TrafficApiAuthError(
                "traffic-api 鉴权失败，请检查 TRAFFIC_API_AUTH_TOKEN",
                status_code=502,
                payload=_safe_payload(resp),
            )
        if resp.status_code == 404:
            raise TrafficApiNotFoundError(
                f"traffic-api 资源不存在: {method} {path}",
                status_code=404,
                payload=_safe_payload(resp),
            )
        if resp.status_code == 409:
            raise TrafficApiConflictError(
                f"traffic-api 状态冲突: {method} {path}",
                status_code=409,
                payload=_safe_payload(resp),
            )
        if resp.status_code == 503:
            raise TrafficApiResourceError(
                f"traffic-api 资源不足（GPU/并发）: {method} {path}",
                status_code=503,
                payload=_safe_payload(resp),
            )
        if 500 <= resp.status_code < 600:
            raise TrafficApiServerError(
                f"traffic-api 服务端错误: {method} {path} — HTTP {resp.status_code}",
                status_code=502,
                payload=_safe_payload(resp),
            )
        # 其他 4xx（422/400 等）—— 尽量提取 traffic-api 的业务消息（detail.message / detail / message）
        safe = _safe_payload(resp)
        detail_msg = None
        if isinstance(safe, dict):
            detail = safe.get("detail")
            if isinstance(detail, dict) and detail.get("message"):
                detail_msg = str(detail["message"])
            elif isinstance(detail, str):
                detail_msg = detail
            elif safe.get("message"):
                detail_msg = str(safe["message"])
        msg = detail_msg or f"traffic-api 错误: {method} {path} — HTTP {resp.status_code}"
        raise TrafficApiError(msg, status_code=resp.status_code, payload=safe)

    # ---- 部署生命周期 ----------------------------------------------

    async def start(self, deployment_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/v1/deployments/{id}/start。返回 {task_id, callback_token, stream_id, ...}。"""
        result = await self._request("POST", f"/api/v1/deployments/{deployment_id}/start", json=payload)
        return result if isinstance(result, dict) else {}

    async def start_status(self, deployment_id: int, task_id: str) -> Dict[str, Any]:
        """GET /api/v1/deployments/{id}/start/status/{task_id}。"""
        result = await self._request(
            "GET", f"/api/v1/deployments/{deployment_id}/start/status/{task_id}"
        )
        return result if isinstance(result, dict) else {}

    async def stop(self, deployment_id: int) -> Dict[str, Any]:
        """POST /api/v1/deployments/{id}/stop。"""
        result = await self._request("POST", f"/api/v1/deployments/{deployment_id}/stop")
        return result if isinstance(result, dict) else {}

    async def stop_status(self, deployment_id: int, task_id: str) -> Dict[str, Any]:
        """GET /api/v1/deployments/{id}/stop/status/{task_id}。"""
        result = await self._request(
            "GET", f"/api/v1/deployments/{deployment_id}/stop/status/{task_id}"
        )
        return result if isinstance(result, dict) else {}

    async def status(self, deployment_id: int) -> Optional[Dict[str, Any]]:
        """GET /api/v1/deployments/{id}/status。404 → None（用于 reconcile 判断 traffic-api 重启后任务记录丢失）。"""
        try:
            result = await self._request("GET", f"/api/v1/deployments/{deployment_id}/status")
        except TrafficApiNotFoundError:
            return None
        return result if isinstance(result, dict) else {}

    async def restart(self, deployment_id: int) -> Dict[str, Any]:
        """POST /api/v1/deployments/{id}/restart。"""
        result = await self._request("POST", f"/api/v1/deployments/{deployment_id}/restart")
        return result if isinstance(result, dict) else {}

    async def restart_status(self, deployment_id: int, task_id: str) -> Dict[str, Any]:
        """GET /api/v1/deployments/{id}/restart/status/{task_id}。"""
        result = await self._request(
            "GET", f"/api/v1/deployments/{deployment_id}/restart/status/{task_id}"
        )
        return result if isinstance(result, dict) else {}

    # ---- 流注册 & 播放 --------------------------------------------

    async def register_streams(self, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """POST /api/v1/stream/devices/register。"""
        result = await self._request(
            "POST", "/api/v1/stream/devices/register", json={"devices": devices}
        )
        return result if isinstance(result, dict) else {}

    async def register_streams_status(self, task_id: str) -> Dict[str, Any]:
        """GET /api/v1/stream/devices/register/status/{task_id}。"""
        result = await self._request("GET", f"/api/v1/stream/devices/register/status/{task_id}")
        return result if isinstance(result, dict) else {}

    async def device_flv_url(self, device_id: int) -> Optional[Dict[str, Any]]:
        """GET /api/v1/stream/device/{id}/flv。404 → None（fallback 到本地文件）。"""
        try:
            result = await self._request("GET", f"/api/v1/stream/device/{device_id}/flv")
        except TrafficApiNotFoundError:
            return None
        return result if isinstance(result, dict) else {}

    # ---- 健康检查 -------------------------------------------------

    async def health(self) -> Dict[str, Any]:
        """GET /api/v1/health。用于 main.py 启动探活与运维监控。"""
        result = await self._request("GET", "/api/v1/health")
        return result if isinstance(result, dict) else {"raw": result}


# ---- 模块级单例（与 ProcessMonitor 单例保持一致） ---------------

_traffic_api_client: Optional[TrafficApiClient] = None


def get_traffic_api_client() -> TrafficApiClient:
    """获取 traffic_api_client 单例（惰性初始化）。"""
    global _traffic_api_client
    if _traffic_api_client is None:
        _traffic_api_client = TrafficApiClient()
    return _traffic_api_client


# ---- 工具 ---------------------------------------------------------

def _safe_payload(resp: httpx.Response) -> Any:
    """尝试解析 JSON 失败时退化为文本，避免日志序列化异常。"""
    try:
        return resp.json()
    except ValueError:
        return resp.text
