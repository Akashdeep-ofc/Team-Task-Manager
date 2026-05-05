from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Annotated
from backend.app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from pydantic import EmailStr

from backend.app.models.models import User, Project, ProjectMember, Task
from backend.app.schemas.project import ProjectOut,ProjectBase

from backend.app.core.security import CurrentUser
from backend.app.api.v1.routes.tasks import router as tasks_router



router = APIRouter(prefix="/project")

router.include_router(router=tasks_router)


@router.post("", response_model=ProjectOut)
def create_project(db: Annotated[Session, Depends(get_db)], user:CurrentUser, project_details:ProjectBase):
    existing=db.execute(
        select(Project).where(
            Project.created_by==user.id,
            func.lower(Project.name)==project_details.name.lower(),
        )).scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project with this name already exists")
    
    project = Project(name=project_details.name, created_by=user.id)
    
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






@router.post("/{project_id}/add")
def add_member(db: Annotated[Session, Depends(get_db)], user:CurrentUser, project_id:int, member_email:Annotated[EmailStr,Body(embed=True)]):

    # check if project exists and admin making changes
    project_found = db.execute(
        select(Project).where(
            Project.id==project_id
        )
    ).scalars().first()

    if not project_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found")
    
    if not (project_found.created_by==user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not Admin")
    
    member = db.execute(
        select(User).where(
            func.lower(User.email)==member_email.lower()
        )
    ).scalars().first()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member doesn't have an Account")
    
    if member.id==user.id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Member cannot be the Admin")
    

    already_member = db.execute(
    select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member.id
        )
    ).scalars().first()

    if already_member:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member already in project")


    member_record = ProjectMember(project_id=project_id,
                  user_id=member.id,)
    
    db.add(member_record)
    db.commit()
    db.refresh(member_record)
    # return {"message":"Member Added Successfully", "Member_details":member_record}
    return {"message":"Member Added Successfully"}



