from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from app.dependencies import SessionDep
from app.users.config import PASSWORD_HASHING_ALGORITHM, PASSWORD_SECRET_KEY
from app.users.crud import get_user_by_username
from app.users.models import TokenDecode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep,
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
        decoded_token = TokenDecode(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(db, username=decoded_token.username)
    if user is None:
        raise credentials_exception

    return user
