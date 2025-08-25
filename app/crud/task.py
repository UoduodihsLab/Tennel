from app.db.models.task import TaskModel
from .base import BaseCRUD
from tortoise.expressions import F
from tortoise.functions import Concat
from typing import List


class TaskCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(TaskModel)

    async def get_with_user_id(self, task_id: int, user_id: int) -> TaskModel | None:
        return await self.model.filter(id=task_id, user_id=user_id).first()

    async def increment_success(self, task_id: int) -> int:
        return await self.model.filter(id=task_id).update(success=F('success') + 1)

    async def increment_failure(self, task_id: int) -> int:
        return await self.model.filter(id=task_id).update(failure=F('failure') + 1)

    async def append_log(self, task_id: int, log: str):
        return await self.model.filter(id=task_id).update(logs=Concat(F('logs'), '\n', log))

    async def filter_by_user_id(self, user_id: int) -> List[TaskModel]:
        return await self.model.filter(user_id=user_id)
