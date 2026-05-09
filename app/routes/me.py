from fastapi import APIRouter, Depends

from app.auth.jwt import get_current_user
from app.db.models import User

router = APIRouter()


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "instagram_connected": bool(current_user.instagram_user_id),
        "gdrive_connected": current_user.gdrive_connected,
        "gdrive_folder_id": current_user.gdrive_folder_id,
        "has_cloudinary": bool(current_user.cloudinary_cloud_name),
    }
