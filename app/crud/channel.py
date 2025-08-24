from app.db.models import ChannelModel
from .base import BaseCRUD
from typing import List


class ChannelCRUD(BaseCRUD[ChannelModel]):
    def __init__(self):
        super().__init__(ChannelModel)

    async def filter_by_user_id(self, user_id: int) -> List[ChannelModel]:
        return await self.model.filter(user_id=user_id)