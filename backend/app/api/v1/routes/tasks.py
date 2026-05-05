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

    





# Get all tasks for a project
@router.get("", response_model=list[TaskOut])
def get_tasks(db: Annotated[Session, Depends(get_db)], user: CurrentUser, project_id: int):
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found")

    # check if user is admin or member of project
    membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        )
    ).scalars().first()


    if not membership:
        raise HTTPException(status_code=403, detail="You Are Not Part Of This Project")
    
    if membership.role=="member":
        tasks = db.execute(
            select(Task).where(
                Task.project_id == project_id,
                Task.assigned_to==user.id
            )
        ).scalars().all()
        return tasks


    tasks = db.execute(
        select(Task).where(Task.project_id == project_id)
    ).scalars().all()
    return tasks




# Update task status — members can do this for their own tasks
@router.patch("/{task_id}", response_model=TaskOut)
def update_task_status(db: Annotated[Session, Depends(get_db)], user: CurrentUser, 
                       project_id: int, task_id: int, new_status: str):
    project = db.execute(select(Project).where(Project.id == project_id)).scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project Does Not Exist")

    task = db.execute(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    ).scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found")

    # Admin can update any task, member can only update their own

    is_admin = project.created_by == user.id
    is_assigned = task.assigned_to == user.id

    if not is_admin and not is_assigned:
        raise HTTPException(status_code=403, detail="Not Authorized")

    if new_status not in ["To Do", "In Progress", "Done"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    task.status = new_status
    db.commit()
    db.refresh(task)
    return task





# Delete task — admin only
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(db: Annotated[Session, Depends(get_db)], user: CurrentUser, 
                project_id: int, task_id: int):
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found")

    if project.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not Authorized")

    task = db.execute(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    ).scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found")

    db.delete(task)
    db.commit()