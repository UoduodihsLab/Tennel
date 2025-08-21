from typing import List

from app.crud.task import TaskCRUD
from app.schemas.common import PageResponse
from app.schemas.task import TaskFilter, TaskResponse


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
