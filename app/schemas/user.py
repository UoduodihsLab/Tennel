from typing import List

from pydantic import BaseModel, Field
from app.constants.enum import UserRole


class UserBase(BaseModel):
    username: str
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=16)


class UserUpdate(BaseModel):
    username: str | None = None


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserResponse(UserBase):
    id: int

    model_config = {
        'from_attributes': True
    }


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]


class UserFilter(BaseModel):
    username: str | None = Field(None, description='按用户名搜索')
    role: UserRole | None = Field(None, description='按角色精确匹配')
