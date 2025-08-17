from typing import List

from fastapi import APIRouter, Depends, status, Query

from app.api.deps import require_admin_role
from app.schemas.common import Pagination, PageResponse
from app.schemas.user import UserResponse, UserCreate, UserFilter
from app.services.user import UserService

service = UserService()

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_admin_role)]
)


@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary='创建新用户')
async def create_user(user_in: UserCreate):
    return await service.create_user(user_in)


@router.get(
    '/',
    response_model=PageResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary='获取用户列表'
)
async def read_users(
        filters: UserFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(
            None,
            title='排序字段',
            description='允许传入多个字段，按顺序排序，如 ?order_by=name&order_by=age'
        ),
):
    total, users = await service.list_users(
        filters=filters,
        page=pagination.page,
        size=pagination.size,
        order_by=order_by,
    )

    return PageResponse[UserResponse](total=total, items=users)


@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK, summary='获取单个用户信息')
async def read_user(user_id: int):
    return await service.get_user_by_id(user_id)
