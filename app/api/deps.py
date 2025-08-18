import logging

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from app.constants.enum import UserRoleEnum
from app.core.config import settings
from app.crud.user import UserCRUD
from app.db.models import UserModel

logger = logging.getLogger(__name__)

user_crud = UserCRUD()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        user_id = payload.get("uid", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail=f"无效的token: 未找到 uid")
    except jwt.ExpiredSignatureError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="token 已过期")
    except jwt.InvalidTokenError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="无效的token")

    user = await user_crud.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="未查询到当前用户记录")

    return user


def require_admin_role(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="非管理员权限")

    return current_user


def auth_dependency(request: Request, user=Depends(get_current_user)):
    request.state.user = user
