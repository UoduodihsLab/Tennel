from typing import List

from app.crud.task import TaskCRUD
from app.schemas.common import PageResponse
from app.schemas.task import TaskFilter, TaskResponse, TaskCreate


class TaskService:
    def __init__(self):
        self.crud = TaskCRUD()

    async def list(self, *, page: int, size: int, filters: TaskFilter, order_by: List[str] | None = None) -> \
            PageResponse[TaskResponse]:
        offset = (page - 1) * size
        filters_dict = filters.model_dump()
        total, rows = await self.crud.list(
            offset=offset,
            limit=size,
            filters=filters_dict,
            order_by=order_by
        )

        items = [TaskResponse.model_validate(row) for row in rows]

        return PageResponse[TaskResponse](total=total, items=items)

    async def create_task(self, user_id: int, data_to_create: TaskCreate) -> TaskResponse:
        dict_to_create = data_to_create.model_dump()
        dict_to_create.update({'user_id': user_id})
        new_task = await self.crud.create(dict_to_create)
        return TaskResponse.model_validate(new_task)

    async def emit_batch_update_username_task(self):
        pass

    async def emit_batch_create_channel_task(self):
        pass

    async def emit_batch_update_about_task(self):
        pass

    async def emit_batch_update_channel_about_task(self):
        pass

    async def emit_batch_update_photo_task(self):
        pass
