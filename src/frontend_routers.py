from typing import Optional

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.core.config import TEMPLATE_DIR

router = APIRouter(tags=["frontend"], include_in_schema=False)
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/")
async def home(request: Request):
    """Redirect to dashboard or login"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login")
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    """Serve registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/verify-email")
async def verify_email_page(request: Request):
    """Serve email verification page"""
    return templates.TemplateResponse("verify-email.html", {"request": request})


@router.get("/todos")
async def todos_page(request: Request):
    """Serve todos page"""
    return templates.TemplateResponse("todos.html", {"request": request})


@router.get("/dashboard")
async def dashboard_page(request: Request):
    """Serve dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/profile")
async def profile_page(request: Request):
    """Serve profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/forgot-password")
async def forgot_password_page(request: Request):
    """Serve forgot password page"""
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@router.get("/reset-password")
async def reset_password_page(request: Request, token: Optional[str] = None):
    """Serve reset password page"""
    return templates.TemplateResponse(
        "reset-password.html", {"request": request, "token": token}
    )
