import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def validate_image_file(file: UploadFile) -> None:
    """Raise HTTP 400 if the file is not a valid image or exceeds the size limit."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: JPEG, PNG, WEBP, HEIC.",
        )


async def save_upload_file(file: UploadFile, subfolder: str = "") -> str:
    """
    Save an uploaded file to the uploads directory.
    Returns the relative path to the saved file.
    """
    upload_dir = Path(settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / filename

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
        )

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path)


def delete_file(file_path: str) -> None:
    """Silently delete a file if it exists."""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
    except Exception:
        pass
