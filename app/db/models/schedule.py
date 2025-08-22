from tortoise import models, fields
from app.db.base import BaseModel
from app.constants.enum import ScheduleType, ScheduleStatus


class ScheduleModel(BaseModel):
    title = fields.CharField(max_length=255)
    s_type = fields.IntEnumField(ScheduleType)
    hour = fields.IntField(range=(0, 24))
    minute = fields.IntField(range=(0, 60))
    second = fields.IntField(range=(0, 60))
    args = fields.JSONField(null=True)
    status = fields.IntEnumField(ScheduleStatus, default=ScheduleStatus.PENDING)

    user = fields.ForeignKeyField('models.UserModel', related_name='schedulers', on_delete=fields.CASCADE)

    class Meta:
        table = 'schedules'
