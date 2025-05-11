from app.core.config import settings

def send_mock_email(to_email: str, otp: str, purpose: str):
    subject = {
        "verify_email": "Verify your Email Address",
        "reset_password": "Reset Your Password"
    }.get(purpose, "Your OTP Code")

    message = f"""
    From: {settings.MAIL_SENDER}
    To: {to_email}
    Subject: {subject}

    Hello,

    Your OTP code for {purpose.replace('_', ' ')} is: {otp}

    This code is valid for {settings.OTP_LIFETIME_MINUTES} minutes.

    Thank you.
    """

    print("[MOCK EMAIL]")
    print(message)
