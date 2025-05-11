from sqlalchemy import Column, String, Integer, DateTime, func, text, Index
from app.db.base import Base  # Use centralized Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)
    email = Column(String, index=True, nullable=False)
    otp = Column(String)
    purpose = Column(String)  # 'verify_email' or 'reset_password'
    expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_otp_email_purpose_created", "email", "purpose", "created_at"),
    )
