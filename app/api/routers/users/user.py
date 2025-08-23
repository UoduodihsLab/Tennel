import logging

from fastapi import APIRouter, Depends, HTTPException, status
from telethon.tl.types import User

from app.api.deps import get_current_user
from app.schemas.user import UserResponse
from app.services.user import UserService

logger = logging.getLogger(__name__)

service = UserService()

router = APIRouter(prefix='/users', tags=['User'])


@router.get('/me/', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(me: User = Depends(get_current_user)):
    try:
        return await service.get_user_by_id(me.id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
