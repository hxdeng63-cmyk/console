import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings


# 占位符检测：默认值中含 "change" 关键字（大小写不敏感）即视为未配置的真实密钥。
# 用于在启动时拦截误用默认值进入生产环境。
_PLACEHOLDER_KEYWORDS = ("change", "change-me")

# 开发/生产环境判定：默认 dev；通过 ENV=production（或 prod/staging）切换为严格模式。
_DEV_ENV_NAMES = {"dev", "development", "local"}


def _is_placeholder(value: str) -> bool:
    """检测值是否仍是占位符（含 change / change-me 关键字）。

    用于在启动时拦截误把硬编码默认值带到生产环境的常见错误。
    """
    lowered = (value or "").lower()
    return any(keyword in lowered for keyword in _PLACEHOLDER_KEYWORDS)


def _is_dev_env() -> bool:
    """当前是否处于开发模式（允许使用占位符默认值）。

    判定依据：环境变量 ENV（兼容 ENVIRONMENT / APP_ENV），默认 dev。
    """
    env = (
        os.getenv("ENV")
        or os.getenv("ENVIRONMENT")
        or os.getenv("APP_ENV")
        or "dev"
    ).lower()
    return env in _DEV_ENV_NAMES


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:e6sWVi7F8c7UneJ5sc586fTy@localhost:5434/ai_console"
    # JWT 签名密钥。必须从环境变量 SECRET_KEY 覆盖；占位符仅在 dev 模式下被放行。
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- traffic-api 集成（外部纯推理服务）---
    # Base URL：traffic-api 监听地址。默认 10000 与 traffic-api Docker 默认端口一致，
    # 严禁与本后端 10088 冲突。
    TRAFFIC_API_BASE_URL: str = "http://127.0.0.1:10000"
    # 设备面鉴权 token：我们的后端 → traffic-api 每个调用带 Authorization: Bearer <此值>。
    # 必须从环境变量 TRAFFIC_API_AUTH_TOKEN 覆盖；占位符仅在 dev 模式下被放行。
    TRAFFIC_API_AUTH_TOKEN: str = "traffic-api-token-change-me-in-production"
    # 默认 callback_url：traffic-api 子进程推送结果的目标地址（SSRF 防护要求必须公网）。
    # 本地开发可留空字符串，traffic-api 不会推送，事件由用户后端单独同步。
    TRAFFIC_API_DEFAULT_CALLBACK_URL: str = ""
    # 单次 HTTP 请求超时（秒）。traffic-api /start 等可能耗时较长，按需调高。
    TRAFFIC_API_REQUEST_TIMEOUT: float = 30.0

    class Config:
        # 用 __file__ 解析绝对路径,避免 uvicorn 启动时 cwd 不是 backend 目录而读不到 .env。
        env_file = str(Path(__file__).resolve().parents[2] / ".env")


def _enforce_real_secrets(settings: Settings) -> None:
    """启动时 fail-fast 校验：禁止把占位符默认值带入非 dev 环境。

    在生产/预发环境如果检测到 SECRET_KEY 或 TRAFFIC_API_AUTH_TOKEN 仍是占位符值，
    立即抛出 RuntimeError（也可用 sys.exit(1)），绝不能让进程继续运行——否则 JWT
    签名可被伪造、traffic-api 鉴权 token 等同公开。
    """
    dev_mode = _is_dev_env()
    offenders: list[str] = []

    if _is_placeholder(settings.SECRET_KEY):
        offenders.append("SECRET_KEY")

    # TRAFFIC_API_AUTH_TOKEN 为空视为占位符（生产必须显式提供），避免静默放行。
    if _is_placeholder(settings.TRAFFIC_API_AUTH_TOKEN) or not settings.TRAFFIC_API_AUTH_TOKEN:
        offenders.append("TRAFFIC_API_AUTH_TOKEN")

    if not offenders:
        return

    if dev_mode:
        # 开发模式仅打印警告，不中断启动，便于本地快速跑通。
        print(
            f"[config] WARNING: using placeholder values for {', '.join(offenders)}; "
            "this is allowed only because ENV is in dev mode.",
            file=sys.stderr,
        )
        return

    env_name = os.getenv("ENV") or os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "dev"
    raise RuntimeError(
        f"{', '.join(offenders)} must be set via environment variables when ENV='{env_name}'. "
        "Refusing to start with placeholder secrets. "
        "Generate strong values with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )


settings = Settings()
_enforce_real_secrets(settings)
