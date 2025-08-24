from typing import List

from fastapi import APIRouter, Depends, status, Query, HTTPException

from app.api.deps import require_admin_role, logger
from app.schemas.common import Pagination, PageResponse
from app.schemas.user import UserResponse, UserCreate, UserFilter
from app.services.user import UserService

service = UserService()

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin_role)]
)


@router.post('/users/', response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary='创建新用户')
async def create_user(user_in: UserCreate):
    try:
        return await service.create_user(user_in)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    '/users/',
    response_model=PageResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary='获取用户列表'
)
async def read_users(
        filters: UserFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(None, title='排序字段', description='允许传入多个字段，按顺序排序')
):
    return await service.list(page=pagination.page, size=pagination.size, filters=filters, order_by=order_by)


@router.get('/users/{user_id}/', response_model=UserResponse, status_code=status.HTTP_200_OK, summary='获取单个用户信息')
async def read_user(user_id: int):
    return await service.get_user_by_id(user_id)
