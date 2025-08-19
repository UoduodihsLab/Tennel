from typing import List

from pydantic import BaseModel, Field


class ChannelResponse(BaseModel):
    id: int
    tid: int
    title: str
    username: str | None = Field(None)
    photo_name: str | None = Field(None)
    about: str | None = Field(None)
    lang: str | None = Field(None)
    primary_links: List[str] | None = Field(None)


class ChannelFilter(BaseModel):
    title: str | None = Field(None)
    username: str | None = Field(None)
    user_id: int | None = Field(None)
