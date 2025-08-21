import logging
import traceback
from typing import List

from certifi.core import exit_cacert_ctx
from fastapi import APIRouter, Depends, status, Request, HTTPException, Query
from starlette.responses import JSONResponse

from app.api.deps import auth_dependency
from app.api.deps import get_client_manager
from app.core.telegram_client import ClientManager
from app.db.models import UserModel
from app.exceptions import UnsupportedTaskTypeError
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


@router.post(
    '/{task_id}/start-task/',
    status_code=status.HTTP_200_OK,
    summary='Start a task'
)
async def start_task(request: Request, task_id: int, client_manager: ClientManager = Depends(get_client_manager)):
    try:
        current_user: UserModel = request.state.user
        await service.start_task(task_id, current_user.id, client_manager)
        return JSONResponse(status_code=status.HTTP_200_OK, content='任务启动成功')
    except UnsupportedTaskTypeError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@router.delete(
    '/{task_id}/',
    status_code=status.HTTP_200_OK,
    summary='Delete a task'
)
async def delete_task(request: Request, task_id: int):
    try:
        current_user: UserModel = request.state.user
        await service.delete_task(task_id, current_user.id)
        return JSONResponse(status_code=status.HTTP_200_OK, content='任务删除成功')
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
