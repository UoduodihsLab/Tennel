from typing import List

from app.crud.user import UserCRUD
from app.exceptions import NotFoundRecordError, AlreadyExistError
from app.schemas.common import PageResponse
from app.schemas.user import UserResponse, UserFilter, UserCreate
from app.utils.security import hash_password


class UserService:
    def __init__(self):
        self.crud = UserCRUD()

    async def get_user_by_id(self, user_id: int) -> UserResponse | None:
        user = await self.crud.get(user_id)

        if user is None:
            raise NotFoundRecordError(f'User {user_id} not found')

        return UserResponse.model_validate(user)

    async def list(self, *, page: int, size: int, filters: UserFilter, order_by: List[str] | None = None) -> \
            PageResponse[UserResponse]:
        offset = (page - 1) * size
        filter_dict = filters.model_dump(exclude_unset=True)
        total, rows = await self.crud.list(offset=offset, limit=size, filters=filter_dict, order_by=order_by)
        items = [UserResponse.model_validate(row) for row in rows]
        return PageResponse[UserResponse](total=total, items=items)

    async def create_user(self, user_in: UserCreate) -> UserResponse | None:
        user_created = await self.crud.get_by_username(user_in.username)

        if user_created:
            raise AlreadyExistError(f'User {user_in.username} already exists')

        hashed_password = hash_password(user_in.password)
        user_dict = {'username': user_in.username, 'hashed_password': hashed_password, 'role': user_in.role}
        new_user = await self.crud.create(user_dict)

        return UserResponse.model_validate(new_user)
