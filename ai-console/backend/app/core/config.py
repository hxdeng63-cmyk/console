from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:e6sWVi7F8c7UneJ5sc586fTy@localhost:5434/ai_console"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- traffic-api 集成（外部纯推理服务）---
    # Base URL：traffic-api 监听地址。默认 10000 与 traffic-api Docker 默认端口一致，
    # 严禁与本后端 10088 冲突。
    TRAFFIC_API_BASE_URL: str = "http://127.0.0.1:10000"
    # 设备面鉴权 token：我们的后端 → traffic-api 每个调用带 Authorization: Bearer <此值>。
    # 部署时通过环境变量覆盖；不要把真实值提交到代码仓库。
    TRAFFIC_API_AUTH_TOKEN: str = "traffic-api-token-change-me-in-production"
    # 默认 callback_url：traffic-api 子进程推送结果的目标地址（SSRF 防护要求必须公网）。
    # 本地开发可留空字符串，traffic-api 不会推送，事件由用户后端单独同步。
    TRAFFIC_API_DEFAULT_CALLBACK_URL: str = ""
    # 单次 HTTP 请求超时（秒）。traffic-api /start 等可能耗时较长，按需调高。
    TRAFFIC_API_REQUEST_TIMEOUT: float = 30.0

    class Config:
        env_file = ".env"


settings = Settings()
