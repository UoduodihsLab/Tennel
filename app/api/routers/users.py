from fastapi import APIRouter, Depends, status, HTTPException, Response

from app.api.deps import require_admin_role
from app.schemas.common import PaginationParamsSchema
from app.schemas.user import UserSchema, UserCreateSchema, UsersSchema, UserFilterParamsSchema, UserUpdateSchema
from app.services.user import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(require_admin_role)]
)


@router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED, summary='创建新用户')
async def create_user(user_in: UserCreateSchema):
    return await user_service.create_user(user_in)


@router.get('/', response_model=UsersSchema, status_code=status.HTTP_200_OK, summary='获取用户列表')
async def read_users(
        filters: UserFilterParamsSchema = Depends(),
        pagination: PaginationParamsSchema = Depends()
):
    total, users = await user_service.get_users_filtered(
        filters=filters,
        page=pagination.page,
        size=pagination.size,
    )

    return UsersSchema(total=total, users=users)


@router.get('/{user_id}', response_model=UserSchema, status_code=status.HTTP_200_OK, summary='获取单个用户信息')
async def read_user(user_id: int):
    db_user = await user_service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='未查询到此用户')

    return db_user


@router.patch('/{user_id}', response_model=UserSchema, status_code=status.HTTP_202_ACCEPTED, summary='更新用户信息')
async def update_user(
        user_id: int,
        user_in: UserUpdateSchema,
):
    db_user = await user_service.get_user_by_id(user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='未查询到此用户')

    return await user_service.update_user(db_user, user_in)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, summary='删除用户')
async def delete_user(user_id: int):
    deleted_count = await user_service.delete_user(user_id=user_id)

    if not deleted_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='未查询到此用户')

    return Response(status_code=status.HTTP_204_NO_CONTENT)
