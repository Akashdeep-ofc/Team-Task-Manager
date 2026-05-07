import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class User(BaseModel):
    username:str

class UserCreate(User):
    email: EmailStr
    password: str
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Password must be at least 8 characters long")

            # raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Password must contain an uppercase letter")

            # raise ValueError("Password must contain an uppercase letter")

        if not re.search(r"[a-z]", value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Password must contain a lowercase letter")

            # raise ValueError("Password must contain a lowercase letter")

        if not re.search(r"\d", value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Password must contain a number")

            # raise ValueError("Password must contain a number")

        return value

class UserOut(User):
    model_config=ConfigDict(from_attributes=True)

    id: int
    email: str





class Token(BaseModel):
    access_token: str
    token_type: str