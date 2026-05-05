from pydantic import BaseModel, EmailStr, ConfigDict

class User(BaseModel):
    username:str

class UserCreate(User):
    email: EmailStr
    password: str


class UserOut(User):
    model_config=ConfigDict(from_attributes=True)

    id: int
    email: str





class Token(BaseModel):
    access_token: str
    token_type: str