# 🔐 Authentication System (FastAPI + Google OAuth2)

A **production-ready authentication system** built using **FastAPI**, providing both **email/password-based login** and **Google OAuth2 sign-in**. Designed with clean architecture, scalability, and modularity in mind. It includes secure practices for handling credentials and user sessions.

This is primarily a **backend-focused** project, but includes a **basic frontend** for Google login testing and demonstration.

---

## 🚀 Features

### Email/Password Authentication

* ✅ Register with name, email, and strong password.
* ✅ Password complexity enforcement: 8+ characters, 1 uppercase, 1 number, 1 special character.
* ✅ Email verification via time-limited OTP.
* ✅ Duplicate email prevention.

### Google Sign-In

* ✅ OAuth2.0 authentication using Google accounts.
* ✅ Auto-linking of Google email to existing accounts.
* ✅ Seamless sign-up and login support.

### Session Management

* ✅ JWT-based stateless session authentication.
* ✅ Secure token blacklisting on logout.

### Password Reset

* ✅ OTP-based password reset flow.
* ✅ Time-limited, secure OTP verification.
* ✅ Password update only after OTP validation.

### Profile Management

* ✅ Fetch logged-in user's profile.
* ✅ Update profile name and upload a profile picture (validated file types).

---

## 🧱 Tech Stack

| Layer          | Technology                          |
| -------------- | ----------------------------------- |
| Backend        | FastAPI                             |
| Authentication | OAuth2 + JWT                        |
| Database       | PostgreSQL + SQLAlchemy (async)     |
| ORM            | SQLAlchemy (async)                  |
| Email          | Mock Email (dev)                    |
| Frontend       | Basic HTML + JS (Google Login demo) |

---

## 📁 Project Structure

```
User-Authentication/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       │   ├── endpoints.py        # /auth routes
│   │       │   ├── schema.py           # Auth request/response models
│   │       │   ├── service.py          # Auth logic (register, login, OTP)
│   │       │   └── repository.py       # DB operations for auth
│   │       └── user/
│   │           ├── endpoints.py        # /user routes (profile)
│   │           ├── schema.py           # User request/response models
│   │           ├── service.py          # Profile logic (image handling)
│   │           └── repository.py       # DB operations for user
│   ├── core/
│   │   ├── config.py                   # Env configuration
│   │   ├── security.py                 # JWT, password hashing, OAuth2
│   │   └── google_oauth.py             # Google OAuth2 integration
│   ├── db/
│   │   ├── base.py                     # SQLAlchemy Base
│   │   ├── session.py                  # Async DB session
│   │   ├── models/
│   │   │   ├── user.py                 # User table
│   │   │   ├── otp.py                  # OTP model
│   │   │   └── blacklisted_token.py    # Logout token blacklist
│   │   └── migrations/
│   │       ├── versions/
│   │       ├── alembic.ini
│   │       ├── env.py
│   │       └── script.py.mako
│   ├── services/
│   │   └── mock_email_service.py       # Mock email sender (for dev)
│   ├── utils/
│   │   ├── hashing.py                  # Password hashing, validators
│   │   └── otp.py                      # OTP generation/validation
│   └── main.py                         # FastAPI app instance
├── static/
│   ├── js/
│   │   └── app_config.js               # Frontend config for Google login
│   ├── profile_images/                # Uploaded user profile pictures
│   └── google_login.html              # Google OAuth frontend (basic)
├── profile_pictures/                  # (Optional) External mount path
├── .gitignore                         # Ignored files for version control
├── .env                               # Environment variables
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
└── myvenv/                            # Python virtual environment (ignored)
```

> Note: The frontend is intentionally minimal and exists only to test and demonstrate Google login integration. The system is frontend-agnostic and can be connected with React, Vue, Angular, etc.

---

## 🔑 API Endpoints

### 🔐 Authentication APIs

| Method | Path                            | Description                   |
| ------ | ------------------------------- | ----------------------------- |
| POST   | `/auth/register`                | Register a new user           |
| POST   | `/auth/login`                   | Login with email/password     |
| POST   | `/auth/logout`                  | Invalidate JWT                |
| POST   | `/auth/resend-verification-otp` | Resend email verification OTP |
| POST   | `/auth/verify-email`            | Verify email with OTP         |
| POST   | `/auth/resend-password-reset-otp`| Resend OTP for password reset   |
| POST   | `/auth/reset-password`          | Reset password using OTP      |

### 🌐 Google OAuth2 APIs

| Method | Path                           | Description                    |
| ------ | ------------------------------ | ------------------------------ |
| GET    | `/api/v1/auth/google-login`    | Redirect to Google OAuth login |
| GET    | `/api/v1/auth/google-callback` | Handle Google login callback   |

### 👤 User Profile APIs

| Method | Path            | Description                    |
| ------ | --------------- | ------------------------------ |
| GET    | `/user/profile` | Fetch current user profile     |
| PATCH  | `/user/profile` | Update name or profile picture |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Divyam07and10/User-Authentication.git
cd User-Authentication
```

### 2. Create `.env`

```ini
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}
SYNC_DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}
SECRET_KEY=your_super_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
OTP_LIFETIME_MINUTES=5
RESEND_COOLDOWN_SECONDS=60
MAIL_SENDER=support@system.com
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
ALGORITHM=HS256
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini revision --autogenerate -m "Add tables"
```

### 5. Start the Development Server

```bash
uvicorn app.main:app --reload
```

---

### 💬 Want to contribute?
- Fork and open a PR!
- Discuss via GitHub Issues or email.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author
Crafted with ❤️ using FastAPI, Google OAuth2, Python, HTML, CSS, and JavaScript.

---

For questions or help, feel free to ask!
