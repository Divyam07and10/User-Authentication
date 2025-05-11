from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.user.models.user import User

async def commit_and_refresh_user(db: AsyncSession, user: User) -> User:
    await db.commit()
    await db.refresh(user)
    return user

async def rollback_transaction(db: AsyncSession):
    await db.rollback()
