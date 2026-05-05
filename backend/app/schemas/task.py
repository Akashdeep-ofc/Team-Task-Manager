from pydantic import BaseModel,ConfigDict
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: str = "To Do"




class TaskOut(TaskBase):
    model_config=ConfigDict(from_attributes=True)

    id:int
    created_by:str
    created_at:datetime
