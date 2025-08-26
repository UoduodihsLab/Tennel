from typing import List

from pydantic import BaseModel, Field


class ChannelResponse(BaseModel):
    id: int
    tid: int | None = Field(None)
    title: str | None = Field(None)
    username: str | None = Field(None)
    link: str | None = Field(None)
    photo: str | None = Field(None)
    description: str | None = Field(None)
    lang: str | None = Field(None)
    primary_link: str | None = Field(None)

    model_config = {
        'from_attributes': True
    }


class ChannelFilter(BaseModel):
    title: str | None = Field(None)
    username: str | None = Field(None)
    user_id: int | None = Field(None)


class SetLang(BaseModel):
    lang: str
    channels_ids: List[int] = Field(..., min_length=1)


class SetPrimaryLink(BaseModel):
    primary_link: str
    channels_ids: List[int] = Field(..., min_length=1)
