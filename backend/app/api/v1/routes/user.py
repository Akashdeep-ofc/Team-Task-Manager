from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from backend.app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from pydantic import EmailStr
from backend.app.models.models import User, Project, ProjectMember, Task
from backend.app.schemas.user import UserCreate, UserOut, Token
from backend.app.schemas.project import ProjectOut
from backend.app.api.v1.routes.projects import router as projects_router


from backend.app.core.security import (
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
    create_access_token,)

from backend.app.core.security import CurrentUser


router = APIRouter()


router.include_router(router=projects_router)



@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(User).where(
            func.lower(User.username) == user.username.lower(),
        ),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = db.execute(
        select(User).where(func.lower(User.email) == user.email.lower()),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        username=user.username,
        email=user.email.lower(),
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user




@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    result = db.execute(
        select(User).where(
            func.lower(User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    # access_token_expires = timedelta(minutes=)
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")




@router.get("/member-projects", response_model=list[ProjectOut])
def get_member_projects(db: Annotated[Session, Depends(get_db)], user: CurrentUser):
    memberships = db.execute(
        select(ProjectMember).where(
            ProjectMember.user_id == user.id,
            ProjectMember.role == "member"  # exclude projects where they are admin
        )
    ).scalars().all()


    projects = [member.project for member in memberships]

    return projects