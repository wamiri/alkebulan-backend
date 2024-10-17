from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.dependencies import SessionDep
from app.users.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    PASSWORD_HASHING_ALGORITHM,
    PASSWORD_SECRET_KEY,
)
from app.users.crud import create_user, get_user_by_username
from app.users.models import TokenEncode, User, UserCreate, UserForm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def signup_user(db: SessionDep, user_form: UserForm):
    hashed_password = get_password_hash(user_form.password)
    user_create = UserCreate(
        username=user_form.username, hashed_password=hashed_password
    )
    create_user(db, user_create)


def login_user(db: SessionDep, user: User):
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = generate_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return TokenEncode(access_token=access_token, token_type="bearer")


def check_if_user_exists(db: SessionDep, username: str):
    return get_user_by_username(db, username)


def authenticate_user(db: SessionDep, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def generate_access_token(data: dict, expires_delta: timedelta | None = None):
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
