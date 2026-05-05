from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from typing import List, Optional
from backend.app.db.base import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)

    # Relationships
    created_projects: Mapped[List["Project"]] = relationship(back_populates="creator")
    tasks_assigned: Mapped[List["Task"]] = relationship(back_populates="assignee")

    memberships: Mapped[List["ProjectMember"]] = relationship(back_populates="user")





class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    # Relationships
    creator: Mapped["User"] = relationship(back_populates="created_projects")
    tasks: Mapped[List["Task"]] = relationship(back_populates="project")
    
    members: Mapped[List["ProjectMember"]] = relationship(back_populates="project")





class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String, default="member")

    # # Relationships
    project: Mapped["Project"] = relationship(
        back_populates="members",
        foreign_keys=[project_id])
    user: Mapped["User"] = relationship(
        back_populates="memberships",
        foreign_keys=[user_id])





class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String, default="To Do")

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    assigned_to: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    # Relationships
    project: Mapped["Project"] = relationship(
        back_populates="tasks",
        foreign_keys=[project_id])
    assignee: Mapped["User"] = relationship(
        foreign_keys=[assigned_to],
        back_populates="tasks_assigned"
    )