from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from backend.app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from pydantic import EmailStr
from backend.app.models.models import User, Project, ProjectMember, Task
from backend.app.schemas.user import UserCreate, UserOut, Token

from backend.app.schemas.project import ProjectOut,ProjectBase
from backend.app.schemas.task import TaskOut, TaskBase


from backend.app.core.security import (
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
    create_access_token,)

from backend.app.core.security import CurrentUser


router = APIRouter()



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






@router.post("/project", response_model=ProjectOut)
def create_project(db: Annotated[Session, Depends(get_db)], user:CurrentUser, project_details:ProjectBase):
    existing=db.execute(
        select(Project).where(
            Project.created_by==user.id,
            func.lower(Project.name)==project_details.name.lower(),
        )).scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Project with this name already exists")
    
    project = Project(name=project_details.name, created_by=user.username)
    
    db.add(project)
    db.flush()
    
    membership = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        role="admin",
    )
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project




@router.post("/project/{project_id}/task", response_model=TaskOut)
def create_task(db: Annotated[Session, Depends(get_db)], user:CurrentUser, task_details:TaskBase, project_id:int):

    # check if project exists
    project_found = db.execute(
        select(Project).where(
            Project.id==project_id
        )
    ).scalars().first()

    if not project_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found")
    
    if not (project_found.created_by==user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not Admin")
    
    
    task = Task(**task_details.model_dump(exclude_none=True),
                project_id=project_id)
    

    db.add(task)
    db.commit()
    db.refresh(task)
    return task
    



@router.post("/project/{project_id}/task/{task_id}")
def assign_task(db: Annotated[Session, Depends(get_db)], user:CurrentUser, project_id:int, task_id:int, member_email:EmailStr):
    
    # check if project exists and admin making changes
    project_found = db.execute(
        select(Project).where(
            Project.id==project_id
        )
    ).scalars().first()

    if not project_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found")
    
    if not (project_found.created_by==user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not Admin")
    
    # checking task exists
    task_found = db.execute(
        select(Task).where(
            Task.id==task_id
        )
    ).scalars().first()

    
    if not task_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found")
    
    if task_found.assigned_to:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already Assigned to Someone")

    member = db.execute(
        select(User).where(
            func.lower(User.email)==member_email.lower()
        )
    ).scalars().first()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member doesn't have an Account")
    
    if member.id==user.id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Member cannot be the Admin")
    
    member_exists = False
    for each in project_found.members:
        if each.user_id==member.id:
            member_exists=True
    
    if not member_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member Is NOT Part Of This Project")


    task_found.assigned_to=member.id

    db.commit()
    db.refresh(task_found)
        
    return {"message":"Task Assigned Successfully", "Task_details":task_found}
    

@router.post("/project/{project_id}/add")
def add_member(db: Annotated[Session, Depends(get_db)], user:CurrentUser, project_id:int, member_email:EmailStr):

    # check if project exists and admin making changes
    project_found = db.execute(
        select(Project).where(
            Project.id==project_id
        )
    ).scalars().first()

    if not project_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found")
    
    if not (project_found.created_by==user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not Admin")
    
    member = db.execute(
        select(User).where(
            func.lower(User.email)==member_email.lower()
        )
    ).scalars().first()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member doesn't have an Account")
    
    if member.id==user.id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Member cannot be the Admin")
    
    member_record = ProjectMember(project_id=project_id,
                  user_id=member.id,)
    
    db.add(member_record)
    db.commit()
    db.refresh(member_record)
    return {"message":"Member Added Successfully", "Member_details":member_record}