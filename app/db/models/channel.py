from tortoise import fields

from app.constants.enum import ChannelStatus, AccountRole
from app.db.base import BaseModel


class ChannelModel(BaseModel):
    tid = fields.BigIntField()
    title = fields.CharField(unique=True, max_length=255)
    username = fields.CharField(unique=True, max_length=64, null=True)
    photo_name = fields.TextField(null=True)
    about = fields.TextField(null=True)

    lang = fields.CharField(max_length=16)
    primary_links = fields.JSONField(null=True)

    status = fields.IntEnumField(ChannelStatus, default=ChannelStatus.UNSYNCED)

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
