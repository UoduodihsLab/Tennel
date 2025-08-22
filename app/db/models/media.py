from tortoise import fields

from app.constants.enum import MediaType
from app.db.base import BaseModel


class MediaModel(BaseModel):
    filename = fields.CharField(max_length=255, unique=True)
    m_type = fields.IntEnumField(MediaType)

    user = fields.ForeignKeyField('models.UserModel', related_name='medias', on_delete=fields.CASCADE)

    class Meta:
        table = 'medias'
