from tortoise import fields

from app.constants.enum import AccountRole
from app.db.base import BaseModel


class ChannelModel(BaseModel):
    tid = fields.BigIntField(unique=True, null=True)
    title = fields.CharField(max_length=255, null=True)
    username = fields.CharField(unique=True, max_length=64, null=True)
    link = fields.CharField(unique=True, max_length=255, null=True)
    photo = fields.TextField(null=True)
    description = fields.TextField(null=True)

    lang = fields.CharField(max_length=16, null=True)
    primary_links = fields.JSONField(null=True)

    is_banned = fields.BooleanField(default=False)

    user = fields.ForeignKeyField('models.UserModel', related_name='channels', on_delete=fields.CASCADE)

    class Meta:
        table = "channels"


class AccountChannelModel(BaseModel):
    account = fields.ForeignKeyField('models.AccountModel', related_name='accounts_channels', on_delete=fields.CASCADE)
    channel = fields.ForeignKeyField('models.ChannelModel', related_name='accounts_channels', on_delete=fields.CASCADE)
    role = fields.IntEnumField(AccountRole)
    access_hash = fields.BigIntField()

    class Meta:
        table = "accounts_channels"
