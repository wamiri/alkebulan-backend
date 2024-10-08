from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.users.config import PASSWORD_HASHING_ALGORITHM, PASSWORD_SECRET_KEY
from app.users.crud import create_user, get_user, get_user_by_username
from app.users.schemas import TokenDecode, UserCreate, UserData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_new_user(db: Session, user: UserCreate):
    return create_user(db, user)


def check_if_user_exists(db: Session, username: str):
    return get_user_by_username(db, username)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        PASSWORD_SECRET_KEY,
        algorithm=PASSWORD_HASHING_ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            PASSWORD_SECRET_KEY,
            algorithms=[PASSWORD_HASHING_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDecode(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[UserData, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
