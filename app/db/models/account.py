from tortoise import fields

from app.db.base import BaseModel


# Telegram 账号
class AccountModel(BaseModel):
    tid = fields.BigIntField(null=True)
    username = fields.CharField(unique=True, max_length=64, null=True)
    phone = fields.CharField(unique=True, max_length=16)
    two_fa = fields.CharField(max_length=32)
    session_name = fields.CharField(unique=True, max_length=16)
    is_authenticated = fields.BooleanField(default=False)
    online = fields.BooleanField(default=False)

    user = fields.ForeignKeyField('models.UserModel', related_name='accounts', on_delete=fields.CASCADE)

    class Meta:
        table = "accounts"
