# api/router/auth.py

from fastapi import APIRouter, status, HTTPException

from app.schemas.auth import LoginData
from app.services.auth import AuthService

service = AuthService()

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login/')
async def login_endpoint(data: LoginData):
    try:
        return await service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
