from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import SessionDep
from app.users.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.users.dependencies import get_current_user
from app.users.models import TokenEncode, UserCreate, UserData, UserForm
from app.users.utils import (
    authenticate_user,
    check_if_user_exists,
    generate_access_token,
    get_password_hash,
    login_user,
    signup_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup")
async def signup(user_form: UserForm, db: SessionDep):
    user = check_if_user_exists(db, username=user_form.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    signup_user(db, user_form)


@router.post("/login")
async def login(
    user_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    response_model=TokenEncode,
):
    user = authenticate_user(db, user_form.username, user_form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    encoded_token = login_user(db, user)
    return encoded_token


@router.get("/me", response_model=UserData)
async def get_profile(
    current_user: Annotated[UserData, Depends(get_current_user)],
):
    return current_user
