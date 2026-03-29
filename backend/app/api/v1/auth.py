from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.schemas.auth import AuthenticatedUser, LoginRequest, TokenResponse
from app.service.auth_service import (
    InvalidCredentialsError,
    authenticate_dev_user,
    issue_access_token,
)
from app.service.token_validator import AuthenticatedPrincipal

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    try:
        user = authenticate_dev_user(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token, expires_in = issue_access_token(user)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=AuthenticatedUser(**user),
    )


@router.get("/me", response_model=AuthenticatedUser)
async def get_me(
    current_user: AuthenticatedPrincipal = Depends(get_current_user),
):
    return AuthenticatedUser(
        user_id=current_user["user_id"],
        subject=current_user["subject"],
        email=current_user["email"],
        name=current_user["name"],
        roles=current_user["roles"],
    )
