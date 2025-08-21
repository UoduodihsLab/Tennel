import logging
from typing import List

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from app.crud.account import AccountCRUD
from app.db.models.account import AccountModel
from app.db.models.user import UserModel
from app.exceptions import AlreadyExistError, AlreadyAuthenticatedError, GetClientError, UpdateRecordError
from app.exceptions import NotFoundRecordError, PermissionDeniedError
from app.schemas.account import (AccountCreate,
                                 AccountResponse,
                                 AccountFilter,
                                 StartLoginResponse,
                                 AccountCompleteLogin, CompleteLoginResponse)
from app.schemas.common import PageResponse
from app.core.telegram_client import get_static_client_for_phone

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self):
        self.crud = AccountCRUD()

    async def create_account(self, user_id: int, data_to_create: AccountCreate):
        created_account = await self.crud.get_by_phone(data_to_create.phone)

        if created_account:
            raise AlreadyExistError('此账号已存在，请勿重复添加')

        dict_to_create = data_to_create.model_dump()

        dict_to_create.update({'session_name': data_to_create.phone, 'user_id': user_id})

        new_account = await self.crud.create(dict_to_create)

        return AccountResponse.model_validate(new_account)

    async def list(self, *, page: int, size: int, filters: AccountFilter, order_by: List[str] | None = None, ) -> \
            PageResponse[AccountResponse]:
        offset = (page - 1) * size
        filters_dict = filters.model_dump(exclude_unset=True)
        total, rows = await self.crud.list(
            offset=offset,
            limit=size,
            filters=filters_dict,
            order_by=order_by
        )

        items = [AccountResponse.model_validate(row) for row in rows]

        return PageResponse[AccountResponse](total=total, items=items)

    async def get_user_account(self, user_id: int, account_id: int) -> AccountModel:
        account = await self.crud.get_with_user(account_id)

        if account is None:
            raise NotFoundRecordError('账号不存在')

        if account.user.id != user_id:
            raise PermissionDeniedError(f'权限错误: {account.user.username} 没有权限操作账号 {account.id}')

        return account

    @staticmethod
    def get_account_client(phone: str) -> TelegramClient:
        try:
            return get_static_client_for_phone(phone)
        except Exception as e:
            raise GetClientError(e) from e

    @staticmethod
    async def ensure_not_authenticated(client, account: AccountModel):
        if await client.is_user_authorized():
            raise AlreadyAuthenticatedError(f'账号{account.user.username}已授登录, 请勿重复登录')

    async def start_login(self, user_id: int, account_id: int) -> StartLoginResponse:
        account = await self.get_user_account(user_id, account_id)
        client = self.get_account_client(account.phone)
        await client.connect()

        try:
            await self.ensure_not_authenticated(client, account)
            sent_code_response = await client.send_code_request(account.phone)
            return StartLoginResponse(phone_code_hash=sent_code_response.phone_code_hash)
        finally:
            if client.is_connected():
                await client.disconnect()

    async def complete_login(
            self,
            user_id: int,
            account_id,
            data_to_complete: AccountCompleteLogin
    ) -> CompleteLoginResponse:
        account = await self.get_user_account(user_id, account_id)
        client = self.get_account_client(account.phone)
        await client.connect()

        account_info = None
        try:
            await self.ensure_not_authenticated(client, account)
            await client.sign_in(phone=account.phone, code=data_to_complete.code,
                                 phone_code_hash=data_to_complete.phone_code_hash)
        except SessionPasswordNeededError as e:
            logger.error(e)
            await client.sign_in(password=account.two_fa)
            account_info = await client.get_me()
        finally:
            if client.is_connected():
                await client.disconnect()

        data_to_update = {
            'tid': account_info.id,
            'username': account_info.username,
            'is_authenticated': True,
        }
        updated = await self.crud.update(account.id, data_to_update)
        if updated < 1:
            raise UpdateRecordError(f'更新 {account.phone} 失败')
        updated_account = await self.crud.get(account.id)
        if updated_account is None:
            raise NotFoundRecordError(f'账号 {account.phone} 在认证过程中被删除')
        return CompleteLoginResponse.model_validate(updated_account)
