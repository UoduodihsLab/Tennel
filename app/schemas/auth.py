from pydantic import BaseModel


class LoginData(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    token_type: str