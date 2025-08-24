# crud/account.py

from typing import List

from app.db.models import AccountModel
from .base import BaseCRUD


class AccountCRUD(BaseCRUD[AccountModel]):
    def __init__(self):
        super().__init__(AccountModel)

    async def get_by_phone(self, phone: str) -> AccountModel | None:
        return await self.model.filter(phone=phone).first()

    async def get_by_session_name(self, session_name: str) -> AccountModel | None:
        return await self.model.filter(session_name=session_name).first()

    async def get_with_user(self, account_id: int) -> AccountModel | None:
        return await self.model.filter(id=account_id).select_related('user').first()

    async def get_all_accounts_session(self) -> List[str]:
        return await self.model.all().values_list('session_name', flat=True)

    async def all(self, user_id: int) -> List[AccountModel]:
        return await self.model.filter(user_id=user_id, is_authenticated=True)
