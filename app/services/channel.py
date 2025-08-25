from typing import List

from app.crud.channel import ChannelCRUD
from app.schemas.channel import ChannelFilter, ChannelResponse
from app.schemas.common import PageResponse


class ChannelService:
    def __init__(self):
        self.crud = ChannelCRUD()

    async def list(self, *, page: int, size: int, filters: ChannelFilter, order_by: List[str] | None = None) -> \
            PageResponse[ChannelResponse]:
        offset = (page - 1) * size
        filter_dict = filters.model_dump(exclude_unset=True)
        total, rows = await self.crud.list(offset=offset, limit=size, filters=filter_dict, order_by=order_by)

        items = [ChannelResponse.model_validate(row) for row in rows]

        return PageResponse[ChannelResponse](total=total, items=items)
