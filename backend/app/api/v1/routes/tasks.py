from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Annotated
from backend.app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from pydantic import EmailStr
from backend.app.models.models import User, Project, ProjectMember, Task

from backend.app.schemas.task import TaskOut, TaskBase
from backend.app.core.security import CurrentUser


router = APIRouter(prefix="/{project_id}/task")



@router.post("", response_model=TaskOut)
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
    



@router.post("/{task_id}")
def assign_task(db: Annotated[Session, Depends(get_db)], user:CurrentUser, project_id:int, task_id:int, member_email:Annotated[EmailStr,Body(embed=True)]):
    print("------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------")
    print("Withing the assign task function")
    print("------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------")

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
    
    # checking task exists
    task_found = db.execute(
        select(Task).where(
            Task.id==task_id,
            Task.project_id==project_id
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
    
    member_exists = db.execute(
    select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member.id
    )
    ).scalars().first()

    if not member_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member Is NOT Part Of This Project")


    task_found.assigned_to=member.id

    db.commit()
    db.refresh(task_found)
        
    # return {"message":"Task Assigned Successfully", "Task_details":task_found}
    return {"message": "Task Assigned Successfully"}

    
