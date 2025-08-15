# api/router/auth.py

from fastapi import APIRouter, HTTPException

from app.schemas.auth import LoginSchema
from app.services.auth import login_service

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login')
async def login_endpoint(data: LoginSchema):
    try:
        return await login_service(data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
