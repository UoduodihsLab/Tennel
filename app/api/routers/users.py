from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import require_admin_role
from app.schemas.common import PaginationParamsSchema
from app.schemas.user import UserResponse, UserCreate, UserListResponse, UserFilter
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


@router.get('/', response_model=UserListResponse, status_code=status.HTTP_200_OK, summary='获取用户列表')
async def read_users(
        filters: UserFilter = Depends(),
        pagination: PaginationParamsSchema = Depends(),
        order_by: List[str] | None = None,
):
    total, users = await service.list_users(
        filters=filters,
        page=pagination.page,
        size=pagination.size,
        order_by=order_by,
    )

    return UserListResponse(total=total, users=users)


@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK, summary='获取单个用户信息')
async def read_user(user_id: int):
    return await service.get_user_by_id(user_id)
