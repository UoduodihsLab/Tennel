from app.db.models.channel import AccountChannelModel
from app.db.models.account import AccountModel
from .base import BaseCRUD

class AccountChannelCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(AccountChannelModel)

    async def count_channels_by_account_id(self, account_id: int) -> int:
        return await self.model.filter(account_id=account_id).count()

    async def get_with_channel_account(self, channel_id: int) -> AccountModel | None:
        return await self.model.filter(channel_id=channel_id).select_related('channel', 'account').first()