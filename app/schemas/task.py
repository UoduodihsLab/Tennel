from typing import Dict, Any, List

from pydantic import BaseModel, Field

from app.constants.enum import TaskType, TaskStatus


class TaskResponse(BaseModel):
    id: int
    title: str
    t_type: TaskType
    args: Dict[str, Any] | None = Field(None)
    status: TaskStatus
    total: int
    success: int
    failure: int
    logs: str | None = Field(None)

    model_config = {
        'from_attributes': True
    }


class TaskCreate(BaseModel):
    title: str
    t_type: TaskType
    args: Dict[str, Any] = Field(...)
    total: int = Field(..., gt=0)


class TaskFilter(BaseModel):
    user_id: int | None = Field(None)
    title: str | None = Field(None)
    t_type: TaskType | None = Field(None)
    status: TaskStatus | None = Field(None)


class BatchCreateChannelArgs(BaseModel):
    account_id: int
    titles: List[str] = Field(..., min_length=1)


class BatchSetChannelUsernameArgs(BaseModel):
    channel_ids: List[int] = Field(..., min_length=1)


class BatchSetChannelPhotoArgs(BaseModel):
    channel_ids: List[int] = Field(..., min_length=1)


class BatchSetChannelDescriptionArgs(BaseModel):
    channel_ids: List[int] = Field(..., min_length=1)
    descriptions: List[str] = Field(..., min_length=1)
