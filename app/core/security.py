from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.api.v1.user.models.user import User
from app.api.v1.auth.models.token_blacklist import TokenBlacklist
from sqlalchemy import select
from typing import Optional
from app.utils.hashing import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    try:
        if not token:
            return None
        return await get_current_user(token, db)
    except HTTPException:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if not email or "@" not in email:
            raise HTTPException(status_code=401, detail="Invalid token format")

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token decoding error: {str(e)}")

    if await TokenBlacklist.is_blacklisted(db, token):
        raise HTTPException(status_code=401, detail="Token revoked")

    result = await db.execute(select(User).where(User.email.ilike(email)))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found. Invalid credentials or revoked token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user