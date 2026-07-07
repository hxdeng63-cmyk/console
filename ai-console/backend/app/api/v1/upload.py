import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/upload", tags=["文件上传"])

# Per migration: uploads now go under data/photo-videos/upload/{images,videos}/
# (separated from detection captures to avoid namespace collision)
UPLOAD_DIR = "/home/daxiong/code/console/data/photo-videos/upload"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/avi", "video/mov", "video/wmv"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image or video file"""
    # Validate file type
    if file.content_type in ALLOWED_IMAGE_TYPES:
        sub_dir = "images"
    elif file.content_type in ALLOWED_VIDEO_TYPES:
        sub_dir = "videos"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}"
        )

    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 (最大 {MAX_FILE_SIZE // (1024*1024)}MB)"
        )

    # Generate unique filename with year/month directory
    ext = file.filename.split(".")[-1] if file.filename else "bin"
    filename = f"{uuid.uuid4().hex}.{ext}"
    now = datetime.now()
    date_dir = f"{now.year}/{now.month:02d}"
    full_dir = os.path.join(UPLOAD_DIR, sub_dir, date_dir)
    os.makedirs(full_dir, exist_ok=True)
    file_path = os.path.join(full_dir, filename)

    # Write file
    with open(file_path, "wb") as f:
        f.write(content)

    # Return URL
    url = f"/data/photo-videos/upload/{sub_dir}/{date_dir}/{filename}"

    return JSONResponse(content={
        "url": url,
        "filename": filename,
        "size": len(content),
        "type": file.content_type,
    })
