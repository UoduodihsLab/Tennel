# crud/account.py

from typing import List

from app.db.models import AccountModel
from .base import BaseCRUD


class AccountCRUD(BaseCRUD[AccountModel]):
    def __init__(self):
        super().__init__(AccountModel)

    async def get_by_phone(self, phone: str) -> AccountModel | None:
        return await self.model.filter(phone=phone).first()

    async def get_related_user(self, account_id: int) -> AccountModel | None:
        return await self.model.filter(id=account_id).select_related('user').first()

    async def list_authenticated_only_session_name(self) -> List[str]:
        return await self.model.filter(is_authenticated=True).values_list('session_name', flat=True)

    async def list_online_by_user_id(self, user_id: int) -> List[AccountModel]:
        return await self.model.filter(user_id=user_id, online=True)

    async def list_online(self) -> List[AccountModel]:
        return await self.model.filter(online=True).select_related('user')

    async def list_authenticated(self) -> List[AccountModel]:
        return await self.model.filter(is_authenticated=True)
