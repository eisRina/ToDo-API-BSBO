
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    nickname: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72
    )


class UserResponse(BaseModel):
    id: int
    nickname: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(
        min_length=8,
        max_length=72
    )
