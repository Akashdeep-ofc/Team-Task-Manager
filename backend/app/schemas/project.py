from pydantic import BaseModel,ConfigDict
from datetime import datetime

class ProjectBase(BaseModel):
    name:str

class ProjectOut(ProjectBase):
    model_config=ConfigDict(from_attributes=True)

    id:int
    created_by:str
    created_at:datetime
