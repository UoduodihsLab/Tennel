import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.constants.enum import UserRoleEnum
from app.core.config import settings
from app.crud.user import user_crud
from app.db.models import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await user_crud.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="未查询到此用户")

    return user


def require_admin_role(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="非管理员权限")

    return current_user
