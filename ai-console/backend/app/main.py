import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.api.v1 import router as api_v1_router
from app.core.database import engine, AsyncSessionLocal
from app.core.database import Base
from app.models.operation_log import OperationLog

# Configure uvicorn/access logging
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not exist)")
    yield
    # Shutdown
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