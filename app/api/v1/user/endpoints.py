from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.session import get_db
from app.api.v1.user.models.user import User
from app.api.v1.user.schema import UserResponse, UpdateUserRequest
from app.api.v1.user.service import save_profile_image, validate_image_type, delete_old_image_if_exists
from app.api.v1.user.repository import commit_and_refresh_user, rollback_transaction

router = APIRouter(prefix="/user", tags=["User"])

@router.patch("/profile", response_model=UserResponse)
async def update_user_profile(
    request: Request,
    payload: UpdateUserRequest = Depends(),
    profile_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if payload.name:
            current_user.name = payload.name

        if profile_image:
            validate_image_type(profile_image)

            if current_user.profile_image:
                delete_old_image_if_exists(current_user.profile_image)

            image_path = await save_profile_image(profile_image, current_user.id)
            current_user.profile_image = image_path

        current_user = await commit_and_refresh_user(db, current_user)

        return UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            profile_image=f"{request.base_url}static/{current_user.profile_image}"
                if current_user.profile_image else None
        )

    except Exception as e:
        await rollback_transaction(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        profile_image=f"{request.base_url}static/{current_user.profile_image}"
            if current_user.profile_image else None
    )
