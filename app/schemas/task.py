from typing import Dict, Any

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
    args: Dict[str, Any] | None = Field(None)


class TaskFilter(BaseModel):
    user_id: int | None = Field(None)
    title: str | None = Field(None)
    t_type: TaskType | None = Field(None)
    args: Dict[str, Any] | None = Field(None)
