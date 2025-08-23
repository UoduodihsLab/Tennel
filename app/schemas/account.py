from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    phone: str
    two_fa: str


class AccountOut(BaseModel):
    id: int
    tid: int | None = Field(None)
    username: str | None = Field(None)
    phone: str
    session_name: str
    is_authenticated: bool
    online: bool

    model_config = {
        'from_attributes': True
    }


class AccountSignIn(BaseModel):
    phone_code_hash: str
    code: str


class SendCodeOut(BaseModel):
    phone_code_hash: str


class AccountSignInOut(AccountOut):
    pass


class AccountFilter(BaseModel):
    user_id: int | None = Field(None)
    status: int | None = Field(None)
