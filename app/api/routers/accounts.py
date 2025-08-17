from typing import List

from fastapi import APIRouter, Depends, status, Query, Request

from app.api.deps import auth_dependency
from app.db.models import UserModel
from app.schemas.account import AccountCreate, AccountResponse, AccountFilter
from app.schemas.common import PageResponse, Pagination
from app.services.account import AccountService

service = AccountService()

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
    dependencies=[Depends(auth_dependency)],
)


@router.post(
    '',
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new account"
)
async def create_account(request: Request, create_data: AccountCreate):
    current_user: UserModel = request.state.user
    return await service.create_account(current_user.id, create_data)


@router.get(
    '',
    response_model=PageResponse[AccountResponse],
    status_code=status.HTTP_200_OK,
    summary="List accounts"
)
async def list_accounts(
        filters: AccountFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(
            None,
            title='排序字段',
            description='允许传入多个字段，按顺序排序，如 ?order_by=name&order_by=age'
        ),
):
    total, accounts = await service.list_accounts(
        filters=filters,
        page=pagination.page,
        size=pagination.size,
        order_by=order_by,
    )

    return PageResponse[AccountResponse](total=total, items=accounts)
