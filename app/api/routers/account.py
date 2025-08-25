import logging
from typing import List

from fastapi import APIRouter, Depends, status, Query, Request, HTTPException
from starlette.responses import JSONResponse

from app.api.deps import auth_dependency, get_client_manager
from app.core.telegram_client import ClientManager
from app.db.models import UserModel
from app.exceptions import AlreadyAuthenticatedError, GetClientError, UpdateRecordError, PermissionDeniedError
from app.schemas.account import AccountCreate, AccountOut, AccountFilter, SendCodeOut, \
    AccountSignIn, AccountSignInOut
from app.schemas.common import PageResponse, Pagination
from app.services.account import AccountService

logger = logging.getLogger(__name__)

service = AccountService()

router = APIRouter(
    prefix="/accounts",
    tags=["Account"],
    dependencies=[Depends(auth_dependency)],
)


@router.post(
    '/',
    response_model=AccountOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create new account"
)
async def create_account(request: Request, create_data: AccountCreate):
    try:
        current_user: UserModel = request.state.user
        return await service.create_account(current_user.id, create_data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    '/',
    response_model=PageResponse[AccountOut],
    status_code=status.HTTP_200_OK,
    summary="List accounts"
)
async def read_accounts(
        request: Request,
        filters: AccountFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(None, title='排序字段', description='允许传入多个字段，按顺序排序')
):
    try:
        current_user: UserModel = request.state.user
        filters.user_id = current_user.id
        return await service.list(page=pagination.page, size=pagination.size, filters=filters, order_by=order_by)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/{account_id}/send-code/',
    response_model=SendCodeOut,
    status_code=status.HTTP_200_OK,
    summary="Start login"
)
async def send_code(request: Request, account_id: int):
    current_user: UserModel = request.state.user

    try:
        return await service.send_code(current_user.id, account_id)
    except PermissionDeniedError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except GetClientError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/{account_id}/sign-in',
    response_model=AccountSignInOut,
    status_code=status.HTTP_200_OK,
    summary="Complete login",
)
async def sign_in(request: Request, account_id: int, data: AccountSignIn):
    current_user: UserModel = request.state.user

    try:
        return await service.sign_in(current_user.id, account_id, data)
    except PermissionDeniedError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (AlreadyAuthenticatedError, GetClientError, UpdateRecordError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    '/{account_id}/launch/',
    status_code=status.HTTP_200_OK,
    summary="Launch account"
)
async def launch(request: Request, account_id: int, client_manager: ClientManager = Depends(get_client_manager)):
    current_user: UserModel = request.state.user
    try:
        await service.launch(current_user.id, account_id, client_manager)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'msg': 'ok'})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    '/{account_id}/unlaunch/',
    status_code=status.HTTP_200_OK,
    summary="Unlaunch account"
)
async def unlaunch(request: Request, account_id: int, client_manager: ClientManager = Depends(get_client_manager)):
    current_user: UserModel = request.state.user
    try:
        await service.unlaunch(current_user.id, account_id, client_manager)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'msg': 'ok'})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
