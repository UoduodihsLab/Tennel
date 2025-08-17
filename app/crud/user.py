# crud/user.py

from app.db.models import UserModel
from .base import BaseCRUD


class UserCRUD(BaseCRUD[UserModel]):
    def __init__(self):
        super().__init__(UserModel)
    async def get_by_username(self, username: str) -> UserModel | None:
        return await self.model.filter(username=username).first()
