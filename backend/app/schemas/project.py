from pydantic import BaseModel,ConfigDict
from datetime import datetime

class ProjectBase(BaseModel):
    name:str

class ProjectOut(ProjectBase):
    model_config=ConfigDict(from_attributes=True)

    id:int
    created_by:int
    created_at:datetime


class ProjectMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    username: str
    email: str
    role: str