from sqlalchemy import Column, String, DateTime, select, delete
from app.db.base import Base
from datetime import datetime

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    token = Column(String, primary_key=True)
    expires_at = Column(DateTime, nullable=False)

    @classmethod
    async def add_to_blacklist(cls, db, token, expires_at):
        result = await db.execute(select(cls).where(cls.token == token))
        existing = result.scalars().first()
        if not existing:
            blacklist_entry = cls(token=token, expires_at=expires_at)
            db.add(blacklist_entry)
            await db.commit()

    @classmethod
    async def is_blacklisted(cls, db, token):
        # Cleanup expired tokens
        await db.execute(delete(cls).where(cls.expires_at < datetime.utcnow()))
        await db.commit()
        result = await db.execute(select(cls).where(cls.token == token))
        return result.scalars().first() is not None