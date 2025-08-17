from fastapi import APIRouter, Depends

from app.api.deps import auth_dependency
from app.schemas.account import AccountCreate
from app.services.account import AccountService

service = AccountService()

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
    dependencies=[Depends(auth_dependency)],
)


@router.post('')
async def create_account(create_data: AccountCreate):
    return await service.create_account(create_data)
