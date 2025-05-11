import os
import aiofiles
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.api.v1.user.models.user import User

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}

async def save_profile_image(file: UploadFile, user_id: int) -> str:
    timestamp = int(datetime.now().timestamp())
    file_ext = file.filename.split('.')[-1]
    filename = f"{user_id}_{timestamp}.{file_ext}"
    file_path = f"static/profile_images/{filename}"
    Path("static/profile_images").mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    return f"profile_images/{filename}"

def validate_image_type(profile_image: UploadFile):
    if profile_image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and GIF images are allowed"
        )

def delete_old_image_if_exists(profile_image_path: str):
    old_path = f"static/{profile_image_path}"
    if os.path.exists(old_path):
        os.remove(old_path)
