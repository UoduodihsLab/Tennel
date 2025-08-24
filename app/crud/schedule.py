from typing import List

from app.db.models.schedule import ScheduleModel
from .base import BaseCRUD


class ScheduleCRUD(BaseCRUD[ScheduleModel]):
    def __init__(self):
        super().__init__(ScheduleModel)

    async def get_join_user_id(self, pk: int, user_id: int) -> ScheduleModel:
        return await self.model.filter(pk=pk, user_id=user_id).first()

    async def filter_by_user_id(self, user_id: int) -> List[ScheduleModel]:
        return await self.model.filter(user_id=user_id)
