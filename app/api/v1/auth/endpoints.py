from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import requests
from app.db.session import get_db
from app.api.v1.user.models.user import User
from app.core.config import settings
from app.api.v1.auth import service
from app.core.google_oauth import get_google_login_url, fetch_user_info_from_google
from app.core.security import oauth2_scheme, get_current_user
from app.api.v1.auth.schema import (
    RegisterRequest, OTPVerifyRequest,
    PasswordResetRequest, PasswordResetVerify, TokenResponse, ResendOTPRequest
)
from app.services.email_service import resend_otp
from app.services.mock_email_service import send_mock_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/google", summary="Initiate Google login")
async def google_login():
    auth_url, _ = get_google_login_url()
    return RedirectResponse(auth_url)

@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(request: Request, code: str, db: AsyncSession = Depends(get_db)):
    try:
        user_info = fetch_user_info_from_google(code)
        access_token = await service.create_or_merge_user_via_google(user_info, db)
        return TokenResponse(access_token=access_token, token_type="bearer")
    except requests.HTTPError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google authentication failed")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Authentication error: {str(e)}")

@router.post("/register")
async def register_user_route(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await service.register_user(payload, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login_user_route(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        return await service.login_user(form_data.username.lower(), form_data.password, db)
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/verify-email")
async def verify_email_route(payload: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await service.verify_email(payload, db)
    except (ValueError, LookupError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/resend-password-reset-otp")
async def resend_password_reset_otp_route(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    return await service.request_password_reset(payload.email.lower(), db)

@router.post("/reset-password")
async def reset_password_route(payload: PasswordResetVerify, db: AsyncSession = Depends(get_db)):
    try:
        return await service.reset_password(payload, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/logout")
async def logout_user_route(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await service.logout_user(token, db)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.post("/resend-verification-otp")
async def resend_verification_otp_route(
    payload: ResendOTPRequest, 
    db: AsyncSession = Depends(get_db)
):
    try:
        otp_value = await resend_otp(db, payload.email.lower(), "verify_email")
        send_mock_email(payload.email.lower(), otp_value, "verify_email")
        return {"msg": "OTP resent successfully"}
    except HTTPException as e:
        # Explicitly pass the detail from the original exception
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
