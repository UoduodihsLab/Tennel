from fastapi import APIRouter, Depends, status, Request, HTTPException, Query
from app.api.deps import auth_dependency
import logging
from typing import List

from app.db.models import UserModel
from app.schemas.common import PageResponse, Pagination
from app.schemas.task import TaskResponse, TaskFilter, TaskCreate
from app.services.task import TaskService

logger = logging.getLogger(__name__)

service = TaskService()

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(auth_dependency)]
)

@router.post(
    '/',
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new task'
)
async def create_new_task(request: Request, data_to_create: TaskCreate):
    current_user: UserModel = request.state.user
    return await service.create_task(current_user.id, data_to_create)


@router.get(
    '/',
    response_model=PageResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get tasks by filter, order_by"
)
async def read_tasks(
        request: Request,
        filters: TaskFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(None, title='排序字段')
):
    current_user: UserModel = request.state.user
    filters.user_id = current_user.id

    return await service.list(page=pagination.page, size=pagination.size, filters=filters, order_by=order_by)