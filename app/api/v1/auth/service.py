from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from app.api.v1.auth import repository
from app.api.v1.user.models.user import User
from app.api.v1.auth.models.otp import OTP
from app.api.v1.auth.models.token_blacklist import TokenBlacklist
from app.utils.hashing import (
    hash_password, verify_password,
    validate_password_strength
)
from app.core.security import create_access_token
from app.services.email_service import generate_otp, resend_otp
from app.services.mock_email_service import send_mock_email
from app.core.config import settings
from app.api.v1.auth.schema import TokenResponse
import jwt

async def create_or_merge_user_via_google(user_info: dict, db: AsyncSession) -> str:
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")
    user = await repository.get_user_by_email(db, email)
    if user:
        user = await repository.update_user_profile_from_google(db, user, name, picture)
    else:
        user = await repository.create_user_from_google(db, email, name, picture)
    token = create_access_token(data={"sub": user.email})
    return token

async def register_user(payload, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    if result.scalars().first():
        raise ValueError("Email already registered")
    validate_password_strength(payload.password)
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    otp_value = generate_otp()
    otp_entry = OTP(
        email=payload.email.lower(),
        otp=otp_value,
        purpose="verify_email",
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_LIFETIME_MINUTES)
    )
    db.add(otp_entry)
    await db.commit()
    send_mock_email(to_email=payload.email.lower(), otp=otp_value, purpose="verify_email")
    return {"msg": "User registered. Please verify your email with the OTP sent."}

async def login_user(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise PermissionError("Invalid credentials")
    if not user.is_verified:
        raise PermissionError("Email not verified")
    token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=token, token_type="bearer")

async def verify_email(payload, db: AsyncSession):
    result = await db.execute(
        select(OTP).where(
            OTP.email == payload.email.lower(),
            OTP.otp == payload.otp,
            OTP.purpose == "verify_email"
        )
    )
    otp_entry = result.scalars().first()
    if not otp_entry or otp_entry.expires_at < datetime.utcnow():
        raise ValueError("Invalid or expired OTP")
    user = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = user.scalars().first()
    if not user:
        raise LookupError("User not found")
    user.is_verified = True
    await db.delete(otp_entry)
    await db.commit()
    return {"msg": "Email verified successfully"}

async def request_password_reset(email: str, db: AsyncSession):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if user:
        otp_value = generate_otp()
        otp_entry = OTP(
            email=email,
            otp=otp_value,
            purpose="reset_password",
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        await db.execute(delete(OTP).where(OTP.email == email, OTP.purpose == "reset_password"))
        db.add(otp_entry)
        await db.commit()
        send_mock_email(email, otp_value, "reset_password")
    return {"msg": "If registered, you'll receive a reset OTP"}

async def reset_password(payload, db: AsyncSession):
    result = await db.execute(
        select(OTP).where(
            OTP.email == payload.email.lower(),
            OTP.otp == payload.otp,
            OTP.purpose == "reset_password"
        )
    )
    otp_entry = result.scalars().first()
    if not otp_entry or otp_entry.expires_at < datetime.utcnow():
        raise ValueError("Invalid or expired OTP")
    user = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = user.scalars().first()
    if not user:
        raise LookupError("User not found")
    validate_password_strength(payload.new_password)
    user.hashed_password = hash_password(payload.new_password)
    await db.delete(otp_entry)
    await db.commit()
    return {"msg": "Password reset successfully"}

async def logout_user(token: str, db: AsyncSession):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
    expires_at = datetime.utcfromtimestamp(payload["exp"])
    await TokenBlacklist.add_to_blacklist(db, token, expires_at)
    await db.commit()
    return {"msg": "Successfully logged out"}

async def request_password_reset(email: str, db: AsyncSession):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if user:
        try:
            otp_value = await resend_otp(db, email, "reset_password")
            send_mock_email(email, otp_value, "reset_password")
        except HTTPException as e:
            raise e  # Propagate cooldown error
    return {"msg": "If registered, you'll receive a reset OTP"}