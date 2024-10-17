from sqlmodel import select

from app.dependencies import SessionDep
from app.users.models import User, UserCreate


def create_user(db: SessionDep, user_create: UserCreate):
    created_user = User.model_validate(user_create)
    db.add(created_user)
    db.commit()
    db.refresh(created_user)


def get_user(db: SessionDep, user_id: int):
    found_user = db.get(User, user_id)
    return found_user


def get_user_by_username(db: SessionDep, username: str):
    statement = select(User).where(User.username == username)
    found_user = db.exec(statement).first()
    return found_user
