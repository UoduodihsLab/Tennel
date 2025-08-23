from passlib.context import CryptContext

from app.crud.user import UserCRUD
from app.exceptions import NotFoundRecordError, UserPasswordError
from app.schemas.auth import LoginData, TokenResponse
from app.utils.security import create_access_token, verify_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.crud = UserCRUD()

    async def login(self, login_data: LoginData):
        user = await self.crud.get_by_username(login_data.username)
        if not user:
            raise NotFoundRecordError("此账号未注册")

        if not verify_password(login_data.password, user.hashed_password):
            raise UserPasswordError('密码错误')

        token_payload = {'sub': user.username, 'uid': user.id, 'role': user.role}
        token = create_access_token(token_payload)
        return TokenResponse.model_validate({'token': token, 'token_type': 'Bearer'})
