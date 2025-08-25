from typing import List, Dict, Any, Tuple

from app.db.models import ChannelModel
from .base import BaseCRUD


class ChannelCRUD(BaseCRUD[ChannelModel]):
    def __init__(self):
        super().__init__(ChannelModel)

    async def filter_by_user_id(self, user_id: int) -> List[ChannelModel]:
        return await self.model.filter(user_id=user_id)

    async def get_by_tid(self, tid: int) -> ChannelModel | None:
        return await self.model.filter(tid=tid).first()

    async def create_or_update_by_tid(self, tid: int, data: Dict[str, Any]) -> Tuple[ChannelModel | None, int]:
        channel = await self.get_by_tid(tid)

        created = None
        updated = 0
        if channel:
            updated = await self.update(channel.id, data)
        else:
            data.update({'tid': tid})
            created = await self.create(data)

        return created, updated
