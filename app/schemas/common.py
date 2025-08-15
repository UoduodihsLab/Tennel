from pydantic import BaseModel, Field


class PaginationParamsSchema(BaseModel):
    page: int = Field(1, ge=1, description='页码')
    size: int = Field(10, ge=0, le=10, description='每页数量')



