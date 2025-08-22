from typing import Dict, Any, List

from pydantic import BaseModel, Field

from app.constants.enum import ScheduleType, ScheduleStatus


class ScheduleIn(BaseModel):
    title: str
    s_type: ScheduleType
    hour: int
    minute: int
    second: int
    args: Dict[str, Any] | None = Field(None)


class ScheduleOut(BaseModel):
    title: str
    s_type: ScheduleType
    hour: int
    minute: int
    second: int
    args: Dict[str, Any] | None = Field(None)
    status: ScheduleStatus

    model_config = {
        'from_attributes': True
    }


class ScheduleFilter(BaseModel):
    user_id: int
    status: ScheduleStatus | None = Field(None)


class PublishMessageArgs(BaseModel):
    min_word_count: int = Field(default=200, ge=200, le=300)
    max_word_count: int = Field(default=300, ge=200, le=300)
    include_imgs: bool = Field(default=False)
    include_videos: bool = Field(default=False)
    include_primary_links: bool = Field(default=False)
    ai_prompt: str = Field(..., description='AI提示词')
    channels_ids: List[int] = Field(..., min_length=1)
