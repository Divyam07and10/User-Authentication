from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    # No ORM mode needed for request models typically

class ResendOTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class TokenResponse(BaseModel): # This model might be created from an object, ensure it's correct
    access_token: str
    token_type: str = "bearer"
    # If TokenResponse is ever created from an ORM object or an object with attributes:
    model_config = ConfigDict(from_attributes=True) 
    
class GoogleToken(BaseModel): # Likely a request model
    code: str

class GoogleUserInfo(BaseModel): # This might be populated from a dict, not ORM
    email: EmailStr
    sub: str # Google ID
    name: str
    # If populated from an object with attributes:
    # model_config = ConfigDict(from_attributes=True)