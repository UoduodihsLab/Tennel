# crud/user.py

from typing import Dict, Tuple, List

from app.db.models import UserModel
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from .base import CRUDBase


class CRUDUser(CRUDBase[UserModel, UserCreateSchema, UserUpdateSchema]):
    async def get_by_username(self, username: str) -> UserModel | None:
        return await self.model.filter(username=username).first()

    async def get_multi_filtered(
            self,
            offset: int,
            limit: int,
            filters: Dict | None = None
    ) -> Tuple[int, List[UserModel]]:

        query = self.model.all()

        if filters:
            clean_filters = {k: v for k, v in filters.items() if v is not None}

            if 'username' in clean_filters:
                username_filter = clean_filters.pop('username')
                query = query.filter(username__icontains=username_filter)

            if clean_filters:
                query = query.filter(**clean_filters)

        total = await query.count()
        rows = await query.offset(offset).limit(limit)

        return total, rows


user_crud = CRUDUser(UserModel)
