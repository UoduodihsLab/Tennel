from tortoise import fields

from app.db.base import BaseModel


# Telegram 账号
class AccountModel(BaseModel):
    tid = fields.BigIntField()
    username = fields.CharField(unique=True, max_length=64)
    phone = fields.CharField(unique=True, max_length=16)
    session_name = fields.CharField(unique=True, max_length=16)

    user = fields.ForeignKeyField('models.UserModel', related_name='accounts', on_delete=fields.CASCADE)

    class Meta:
        table = "accounts"
