from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.models import User
from backend.app.schemas.user import UserCreate
from backend.app.core.security import hash_password, verify_password


def create_user(db: Session, user_data: UserCreate):
    existing_user = db.query(User).filter(func.lower(User.email) == user_data.email.lower).first()
    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user