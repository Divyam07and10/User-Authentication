import random
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth.models.otp import OTP
from app.core.config import settings
from sqlalchemy import select, delete

def generate_otp():
    return str(random.randint(100000, 999999))

def create_otp(email: str, purpose: str) -> OTP:
    now = datetime.utcnow()
    return OTP(
        email=email,
        otp=generate_otp(),
        purpose=purpose,
        expires_at=now + timedelta(minutes=settings.OTP_LIFETIME_MINUTES)
    )

async def resend_otp(db: AsyncSession, email: str, purpose: str) -> str:
    now = datetime.utcnow()  # Use UTC for all timestamps

    # 1. Fetch the most recent OTP for this email/purpose
    result = await db.execute(
        select(OTP)
        .where(OTP.email == email, OTP.purpose == purpose)
        .order_by(OTP.created_at.desc())
    )
    last_otp = result.scalars().first()

    # 2. Enforce cooldown period (60 seconds)
    if last_otp:
        cooldown_end = last_otp.created_at + timedelta(seconds=settings.RESEND_COOLDOWN_SECONDS)
        remaining = (cooldown_end - now).total_seconds()
        if remaining > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {int(remaining)} seconds before resending."
            )

    # 3. Delete all existing OTPs for this email/purpose
    await db.execute(
        delete(OTP).where(OTP.email == email, OTP.purpose == purpose)
    )
    await db.commit()  # Ensure deletions are persisted

    # 4. Create a new OTP
    new_otp = OTP(
        email=email,
        otp=generate_otp(),
        purpose=purpose,
        expires_at=now + timedelta(minutes=settings.OTP_LIFETIME_MINUTES),
        created_at=now  # Explicit UTC timestamp
    )
    db.add(new_otp)
    await db.flush()  # Assigns the OTP value without committing
    otp_value = new_otp.otp  # Capture the OTP value
    await db.commit()  # Final commit

    return otp_value