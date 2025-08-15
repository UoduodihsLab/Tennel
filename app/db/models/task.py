from tortoise import fields

from app.constants.enum import TaskType, TaskStatus
from app.db.base import BaseModel


class TaskModel(BaseModel):
    title = fields.CharField(unique=True, max_length=255)
    t_type = fields.IntEnumField(TaskType)
    args = fields.JSONField(null=True)
    status = fields.IntEnumField(TaskStatus, default=TaskStatus.PENDING)
    total = fields.IntField()
    success = fields.IntField(default=0)
    failure = fields.IntField(default=0)
    logs = fields.TextField(null=True)

    user = fields.ForeignKeyField('models.UserModel', related_name='tasks', on_delete=fields.CASCADE)

    class Meta:
        table = "tasks"
