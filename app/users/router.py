from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.users.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.users.models import users_db
from app.users.schemas import Token, User
from app.users.utils import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me/", response_model=User)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
