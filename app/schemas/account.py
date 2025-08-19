from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    phone: str
    two_fa: str


class AccountResponse(BaseModel):
    id: int
    tid: int | None = Field(None)
    username: str | None = Field(None)
    phone: str
    session_name: str

    model_config = {
        'from_attributes': True
    }


class AccountCompleteLogin(BaseModel):
    phone_code_hash: str
    code: str


class StartLoginResponse(BaseModel):
    phone_code_hash: str


class CompleteLoginResponse(AccountResponse):
    pass


class AccountFilter(BaseModel):
    user_id: int | None = Field(None)
    status: int | None = Field(None)
