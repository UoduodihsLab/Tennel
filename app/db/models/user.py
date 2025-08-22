from tortoise import fields

from app.db.base import BaseModel
from app.constants.enum import UserRole


# 系统用户
class UserModel(BaseModel):
    username = fields.CharField(unique=True, max_length=255)
    hashed_password = fields.CharField(max_length=128)
    role = fields.IntEnumField(UserRole, null=True)
    class Meta:
        table = "users"
