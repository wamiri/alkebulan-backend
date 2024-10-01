from app.database import SessionLocal, engine
from app.users import models as users_models

users_models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
