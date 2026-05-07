from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Annotated
from datetime import datetime, UTC
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, select, delete, update
from pydantic import EmailStr

from app.models.models import User, Project, ProjectMember, Task
from app.schemas.project import ProjectOut,ProjectBase, ProjectMemberOut
from app.schemas.task import TaskOut, TaskBase

from app.core.security import CurrentUser

router = APIRouter(prefix="")




@router.get("/{project_id}/admin-dashboard-summary")
def get_dashboard(db: Annotated[Session, Depends(get_db)], user: CurrentUser, project_id: int):
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found")

    if project.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not Authorized")

    tasks = db.execute(
        select(Task).where(Task.project_id == project_id)
    ).scalars().all()

    now = datetime.now(UTC)

    return {
        "total_tasks": len(tasks),
        "by_status": {
            "To Do": sum(1 for t in tasks if t.status == "To Do"),
            "In Progress": sum(1 for t in tasks if t.status == "In Progress"),
            "Done": sum(1 for t in tasks if t.status == "Done"),
        },
        "tasks_per_user": {
            t.assignee.username: sum(1 for task in tasks if task.assigned_to == t.assigned_to)
            for t in tasks if t.assigned_to
        },
        "overdue_tasks": [
            t for t in tasks 
            if t.due_date and t.due_date.replace(tzinfo=UTC) < now and t.status != "Done"
        ]
    }




@router.get("/{project_id}/member-dashboard-summary")
def member_dashboard(db: Annotated[Session, Depends(get_db)], user: CurrentUser, project_id: int):
    tasks = db.execute(
        select(Task).where(
            Task.project_id == project_id,
            Task.assigned_to == user.id
        )
    ).scalars().all()

    now = datetime.now(UTC)

    return {
        "total_assigned": len(tasks),
        "by_status": {
            "To Do": sum(1 for t in tasks if t.status == "To Do"),
            "In Progress": sum(1 for t in tasks if t.status == "In Progress"),
            "Done": sum(1 for t in tasks if t.status == "Done"),
        },
        "overdue": [t for t in tasks if t.due_date and t.due_date.replace(tzinfo=UTC) < now and t.status != "Done"]
    }






# Tasks filtered by status
def get_tasks_by_status(db: Annotated[Session, Depends(get_db)], user: CurrentUser, 
                        project_id: int):
    status_list:list[str] = ["To Do", "In Progress", "Done"]
    grouped_by_status={}
    for task_status in status_list:
        grouped_by_status[task_status]= get_tasks_by_single_status(db=db, user=user, project_id=project_id, task_status=task_status)

    return grouped_by_status
     


def get_tasks_by_single_status(db: Annotated[Session, Depends(get_db)], user: CurrentUser, 
                        project_id: int, task_status: str):
    
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found")
    
    membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        )
    ).scalars().first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not Part Of This Project")

    if task_status not in ["To Do", "In Progress", "Done"]:
        raise HTTPException(status_code=400, detail="Invalid status provided")

    # admin sees all, member sees only their own
    query = select(Task).where(Task.project_id == project_id, Task.status == task_status)
    if membership.role == "member":
        query = query.where(Task.assigned_to == user.id)

    return db.execute(query).scalars().all()





# List of OverDue Tasks
def get_overdue_tasks(db: Annotated[Session, Depends(get_db)], user: CurrentUser, project_id: int):

    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project Not Found")


    membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        )
    ).scalars().first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not Part Of This Project")

    now = datetime.now(UTC)
    query = select(Task).where(
        Task.project_id == project_id,
        Task.due_date.isnot(None),
        Task.due_date < now,
        Task.status != "Done"
    )
    if membership.role == "member":
        query = query.where(Task.assigned_to == user.id)

    return db.execute(query).scalars().all()





def get_tasks_per_user(db: Annotated[Session, Depends(get_db)], user: CurrentUser,
                       project_id: int):
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalars().first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found")

    if project.created_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only allowed")

    tasks = db.execute(
        select(Task).where(
            Task.project_id == project_id,
            Task.assigned_to.is_not(None)
        )
        .order_by(Task.assigned_to)
    ).scalars().all()
    
    grouped_by_members = {}
    for task in tasks:
        key =  task.assignee.username
        if key not in grouped_by_members:
            grouped_by_members[key]=[]
        grouped_by_members[key].append(task)


    return grouped_by_members






def filter_tasks(db: Annotated[Session, Depends(get_db)], user: CurrentUser, project_id: int, task_status:bool, overdue:bool, per_user:bool):
    if sum([task_status, overdue, per_user])!=1:
        raise HTTPException(status_code=417, detail="Expect only one condition to be true")
    
    
    if task_status:
        return get_tasks_by_status(db=db,user=user, project_id=project_id)
    if overdue:
        return get_overdue_tasks(db=db,user=user, project_id=project_id)
    if per_user:
        return get_tasks_per_user(db=db,user=user, project_id=project_id)

    return