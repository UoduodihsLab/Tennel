# api/router/auth.py

from fastapi import APIRouter, status, HTTPException

from app.exceptions import UserPasswordError
from app.schemas.auth import LoginData
from app.services.auth import AuthService
import logging

logger = logging.getLogger(__name__)

service = AuthService()

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/login/')
async def login_endpoint(data: LoginData):
    try:
        return await service.login(data)
    except UserPasswordError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
