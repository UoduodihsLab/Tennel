from typing import List, Tuple

from app.crud.account import AccountCRUD
from app.exceptions import AlreadyExistError
from app.schemas.account import AccountCreate, AccountResponse, AccountFilter


class AccountService:
    def __init__(self):
        self.crud = AccountCRUD()

    async def create_account(self, user_id: int, create_data: AccountCreate):
        created_account = await self.crud.get_by_phone(create_data.phone)

        if created_account:
            raise AlreadyExistError('此账号已存在，请勿重复添加')

        create_dict = create_data.model_dump()

        create_dict.update({'session_name': create_data.phone, 'user_id': user_id})

        new_account = await self.crud.create(create_dict)

        return AccountResponse.model_validate(new_account)

    async def list_accounts(
            self,
            filters: AccountFilter,
            page: int,
            size: int,
            order_by: List[str] | None = None,
    ) -> Tuple[int, List[AccountResponse]]:
        offset = (page - 1) * size
        filter_dict = filters.model_dump(exclude_unset=True)
        total, rows = await self.crud.list_filtered(
            offset=offset,
            limit=size,
            filters=filter_dict,
            order_by=order_by
        )

        accounts = [AccountResponse.model_validate(row) for row in rows]

        return total, accounts
