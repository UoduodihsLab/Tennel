from app.db.models.channel import AccountChannelModel
from app.db.models.account import AccountModel
from .base import BaseCRUD

class AccountChannelCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(AccountChannelModel)

    async def count_channels_by_account(self, account_id: int) -> int:
        return await self.model.filter(account_id=account_id).count()