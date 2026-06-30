import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.api.v1 import router as api_v1_router
from app.core.database import engine, AsyncSessionLocal
from app.core.database import Base
from app.models.deployment import Deployment
from app.models.operation_log import OperationLog
from app.services.process_monitor import ProcessMonitor

# Register SQLAlchemy event监听器 (WarningEvent -> File 更新同步)
from app.models.events import sync_file_records_on_update

# Configure uvicorn/access logging
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def _update_deployment_status(
    deployment_id: int,
    status: str,
    pid: int | None,
    token: str | None = None,
) -> None:
    """Callback used by ProcessMonitor to persist deployment status changes.

    `token` is forwarded when the monitor rotated the deployment_token
    (e.g. on a watchdog restart). When provided, we must persist the new
    value so subsequent ingest requests with the rotated token succeed.
    """
    try:
        async with AsyncSessionLocal() as db:
            deployment = await db.get(Deployment, deployment_id)
            if deployment is None:
                return
            deployment.algorithm_status = status
            deployment.pid = pid
            if token is not None:
                deployment.deployment_token = token
            if status == "running":
                deployment.started_at = datetime.utcnow()
                deployment.stopped_at = None
            elif status in ("stopped", "error", "crashed", "completed"):
                deployment.stopped_at = datetime.utcnow()
            await db.commit()
    except Exception:
        logger.exception("Failed to update deployment %s status to %s", deployment_id, status)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not exist)")

    # Start scheduled cleanup job
    from app.core.scheduler import start_scheduler
    start_scheduler()

    # Reconcile any zombie deployments left by a previous backend process
    monitor = ProcessMonitor()
    async with AsyncSessionLocal() as db:
        await monitor.reconcile(db)
    logger.info("Deployment process reconciliation completed")

    # Register DB status callback and start the watchdog loop.
    monitor.register_status_callback(_update_deployment_status)
    monitor.start_watchdog()
    logger.info("ProcessMonitor watchdog started")

    yield

    # Shutdown
    from app.core.scheduler import shutdown_scheduler
    shutdown_scheduler()
    await monitor.stop_watchdog()
    await engine.dispose()


app = FastAPI(title="AI Console API", version="1.0.0", lifespan=lifespan)

# Static files for uploads
UPLOAD_DIR = "/home/daxiong/code/console/docs"
os.makedirs(os.path.join(UPLOAD_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "videos"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(api_v1_router, prefix="/api/v1")


# Operation log middleware — records every API request
@app.middleware("http")
async def operation_log_middleware(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)

    # Skip health checks, docs, and static assets
    path = request.url.path
    if path in ("/health", "/docs", "/openapi.json") or path.startswith("/static"):
        return response

    # Extract username from Authorization header (if present)
    username = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            from jose import jwt
            from app.core.config import settings
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("username")
        except Exception:
            pass

    # Async fire-and-forget log write
    try:
        async with AsyncSessionLocal() as db:
            log = OperationLog(
                username=username,
                method=request.method,
                path=path,
                ip=request.client.host if request.client else None,
                status_code=response.status_code,
                result="success" if response.status_code < 400 else "failed",
                description="API request",
                action_time=start_time,
            )
            db.add(log)
            await db.commit()
    except Exception:
        # Never fail the main request because logging failed
        pass

    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
