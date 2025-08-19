import logging
from typing import List

from fastapi import APIRouter, Depends, status, Query, Request, HTTPException

from app.api.deps import auth_dependency
from app.db.models import UserModel
from app.exceptions import AlreadyAuthenticatedError, GetClientError, UpdateRecordError, PermissionDeniedError
from app.schemas.account import AccountCreate, AccountResponse, AccountFilter, StartLoginResponse, \
    AccountCompleteLogin, CompleteLoginResponse
from app.schemas.common import PageResponse, Pagination
from app.services.account import AccountService

logger = logging.getLogger(__name__)

service = AccountService()

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
    dependencies=[Depends(auth_dependency)],
)


@router.post(
    '/',
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new account"
)
async def create_account(request: Request, create_data: AccountCreate):
    current_user: UserModel = request.state.user
    return await service.create_account(current_user.id, create_data)


@router.get(
    '/',
    response_model=PageResponse[AccountResponse],
    status_code=status.HTTP_200_OK,
    summary="List accounts"
)
async def read_accounts(
        request: Request,
        filters: AccountFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(None, title='排序字段', description='允许传入多个字段，按顺序排序')
):
    current_user: UserModel = request.state.user
    filters.user_id = current_user.id
    return await service.list(page=pagination.page, size=pagination.size, filters=filters, order_by=order_by)


@router.post(
    '/{account_id}/start-login',
    response_model=StartLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Start login"
)
async def start_login(request: Request, account_id: int):
    current_user: UserModel = request.state.user

    try:
        return await service.start_login(current_user, account_id)
    except PermissionDeniedError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except GetClientError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    '/{account_id}/complete-login',
    response_model=CompleteLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete login",
)
async def complete_login(request: Request, account_id: int, data: AccountCompleteLogin):
    current_user: UserModel = request.state.user

    try:
        return await service.complete_login(current_user, account_id, data)
    except PermissionDeniedError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (AlreadyAuthenticatedError, GetClientError, UpdateRecordError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
