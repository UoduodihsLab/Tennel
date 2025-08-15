from typing import List

from pydantic import BaseModel, Field
from app.constants.enum import UserRoleEnum


class UserBaseSchema(BaseModel):
    username: str
    role: UserRoleEnum


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=6, max_length=64)


class UserUpdateSchema(BaseModel):
    username: str | None = None


class UserChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str


class UserSchema(UserBaseSchema):
    id: int

    model_config = {
        'from_attributes': True
    }


class UsersSchema(BaseModel):
    total: int
    users: List[UserSchema]


class UserFilterParamsSchema(BaseModel):
    username: str | None = Field(None, description='按用户名搜索')
    role: UserRoleEnum | None = Field(None, description='按角色精确匹配')


