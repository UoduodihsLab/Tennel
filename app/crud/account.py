# crud/account.py

from app.db.models import AccountModel
from .base import BaseCRUD


class AccountCRUD(BaseCRUD[AccountModel]):
    def __init__(self):
        super().__init__(AccountModel)

    async def get_by_phone(self, phone: str) -> AccountModel | None:
        return await self.model.filter(phone=phone).first()
