from typing import Tuple, List

from app.crud.user import user_crud
from app.db.models.user import UserModel
from app.schemas.user import UserFilterParamsSchema, UserCreateSchema, UserUpdateSchema, UserSchema
from app.utils.security import hash_password


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: int) -> UserModel | None:
        return await user_crud.get(pk=user_id)

    @staticmethod
    async def get_users_filtered(
            filters: UserFilterParamsSchema,
            page: int,
            size: int
    ) -> Tuple[int, List[UserModel]]:
        offset = (page - 1) * size
        filter_dict = filters.model_dump(exclude_unset=True)
        total, users = await user_crud.get_multi_paginated_filtered(
            offset=offset,
            limit=size,
            filters=filter_dict,
        )

        return total, users

    @staticmethod
    async def create_user(
            user_in: UserCreateSchema,
    ) -> UserModel | None:
        # TODO: 检查用户名是否已经存在

        create_data_dict = user_in.model_dump()
        create_data_dict['hashed_password'] = hash_password(create_data_dict.pop('password'))

        return await user_crud.create(**create_data_dict)

    @staticmethod
    async def update_user(user: UserModel, user_in: UserUpdateSchema) -> UserModel:
        return await user_crud.update(db_obj=user, data=user_in)

    @staticmethod
    async def delete_user(user_id: int) -> int:
        return await user_crud.remove(pk=user_id)


user_service = UserService()
