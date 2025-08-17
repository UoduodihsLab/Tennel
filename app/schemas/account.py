from pydantic import BaseModel, Field

from app.db.models import AccountModel


class AccountCreate(BaseModel):
    phone: str
    two_fa: str


class AccountResponse(BaseModel):
    tid: int | None
    username: str | None
    phone: str
    session_name: str


class AccountStartLogin(BaseModel):
    phone: str = Field(..., description='手机号')


class AccountCompleteLogin(BaseModel):
    phone: str
    phone_code_hash: str
    code: str
    two_fa: str | None = Field(None)


class StartLoginResponse(BaseModel):
    phone_code_hash: str

