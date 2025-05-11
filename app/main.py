from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.user import endpoints as user_endpoints
from app.api.v1.auth import endpoints as auth_endpoints
from app.core.config import settings

app = FastAPI()

# Mount static files first
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root_redirect(request: Request):
    return RedirectResponse(url=request.url_for("static", path="/google_login.html"), status_code=302)

app.include_router(auth_endpoints.router)
app.include_router(user_endpoints.router)