from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import BackgroundTasks
from app.services.email_service import EmailService
from app.services.auth_service import (
    register_user,
    login,
    verify_email,
    resend_verification,
)
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, VerifyEmailRequest
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

in_production = settings.environment == "production"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=in_production,
        samesite="none",
        max_age=900,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=in_production,
        samesite="none",
        path="/api/auth/refresh",
        max_age=900,
    )


@router.post("/register", status_code=201)
async def register_route(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    email_service = EmailService(background_tasks)
    return await register_user(db, payload, email_service)


@router.post("/verify-email")
async def verify_email_route(
    payload: VerifyEmailRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    tokens = await verify_email(db, payload.email, payload.code)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return {"message": "Email verified successfully"}


@router.post("/login")
async def login_route(
    payload: LoginRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    email_service = EmailService(background_tasks)
    tokens = await login(db, payload, email_service)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return {"message": "Logged in successfully"}


@router.post("/resend-verification")
async def resend_verification_code_route(
    email: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    email_service = EmailService(background_tasks)
    await resend_verification(db, email, email_service)


@router.post("/logout")
async def logout_route(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
