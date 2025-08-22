from pydantic import BaseModel, Field

from app.constants.enum import MediaType


class MediaCreate(BaseModel):
    m_type: MediaType


class MediaResponse(BaseModel):
    filename: str
    m_type: MediaType

    model_config = {
        'from_attributes': True
    }


class MediaFilter(BaseModel):
    user_id: int | None = Field(None)
    filename: str | None = None
    m_type: MediaType | None = Field(None)
