# app/api/v1/user/schema.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from fastapi import Form

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    profile_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None 