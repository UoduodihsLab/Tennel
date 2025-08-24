from typing import List

from app.constants.enum import AccountRole
from app.crud.account import AccountCRUD
from app.crud.account_channel import AccountChannelCRUD
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

    async def create_channel_with_account(
            self,
            user_id: int,
            tid: int,
            title,
            access_hash: int,
            role: AccountRole,
            session_name: str
    ):
        data_to_create = {'tid': tid, 'title': title, 'user_id': user_id}
        created_channel = await self.crud.create(data_to_create)
        account = await AccountCRUD().get_by_session_name(session_name)
        await AccountChannelCRUD().create(
            {
                'account': account,
                'channel': created_channel,
                'role': role,
                'access_hash': access_hash,
            }
        )

    async def all_channels(self, user_id: int) -> List[ChannelResponse]:
        rows = await self.crud.all(user_id=user_id)

        items = [ChannelResponse.model_validate(row) for row in rows]

        return items
