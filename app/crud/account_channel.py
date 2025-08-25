from app.db.models.channel import AccountChannelModel
from app.db.models.account import AccountModel
from .base import BaseCRUD
from app.constants.enum import AccountRole

class AccountChannelCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(AccountChannelModel)

    async def count_created_channels(self, account_id: int) -> int:
        return await self.model.filter(account_id=account_id, role=AccountRole.OWNER).count()

    async def get_with_channel_account(self, channel_id: int) -> AccountModel | None:
        return await self.model.filter(channel_id=channel_id).select_related('channel', 'account').first()

    async def get_by_channel_id_and_account_id(self, channel_id: int, account_id: int) -> AccountModel | None:
        return await self.model.filter(channel_id=channel_id, account_id=account_id).first()