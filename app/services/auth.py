from passlib.context import CryptContext
from telethon.errors import NotFoundError

from app.crud.user import UserCRUD
from app.schemas.auth import LoginData, TokenResponse
from app.utils.security import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.crud = UserCRUD()

    async def login(self, login_data: LoginData):
        user = await self.crud.get_by_username(login_data.username)
        if not user:
            raise NotFoundError("User not found")

        token_payload = {'sub': user.username, 'uid': user.id, 'role': user.role}
        token = create_access_token(token_payload)
        return TokenResponse.model_validate({'token': token, 'token_type': 'bearer'})
