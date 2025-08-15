from passlib.context import CryptContext

from app.crud.user import user_crud
from app.schemas.auth import LoginSchema, TokenOutSchema

from app.utils.security import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def login_service(data: LoginSchema):
    user = await user_crud.get_by_username(data.username)
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise ValueError("Invalid username or password")

    token_data = {'sub': str(user.id)}
    token = create_access_token(token_data)

    token_out = TokenOutSchema.model_validate({'token': token, 'token_type': 'bearer'})
    return token_out
