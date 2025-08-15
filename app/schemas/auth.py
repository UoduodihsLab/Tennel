from pydantic import BaseModel


class LoginSchema(BaseModel):
    username: str
    password: str


class TokenOutSchema(BaseModel):
    token: str
    token_type: str