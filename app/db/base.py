from sqlalchemy.orm import declarative_base
Base = declarative_base()
from app.api.v1.auth.models import otp, token_blacklist
from app.api.v1.user.models import user