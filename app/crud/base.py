# crud/base.py

from typing import Type, TypeVar, Generic, Dict, List, Tuple, Any

from pydantic import BaseModel
from tortoise.models import Model

ModelType = TypeVar('ModelType', bound=Model)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, pk: Any) -> ModelType | None:
        return await self.model.filter(pk=pk).first()

    async def get_multi(self, offset: int = 0, limit: int = 10) -> List[ModelType]:
        return await self.model.all().offset(offset).limit(limit)

    async def get_multi_paginated_filtered(
            self,
            offset: int = 0,
            limit: int = 10,
            filters: Dict | None = None,
            order_by: List[str] | None = None,
    ) -> Tuple[int, List[ModelType]]:
        """
        分页, 过滤, 排序
        :param offset:
        :param limit:
        :param filters:
        :param order_by:
        :return:
        """
        query = self.model.all()

        if filters:
            clean_filters = {k: v for k, v in filters.items() if v is not None}
            if clean_filters:
                query = query.filter(**clean_filters)

        total = await query.count()

        if order_by:
            query = query.order_by(*order_by)

        rows = await query.offset(offset).limit(limit)

        return total, rows

    async def create(self, data: CreateSchemaType) -> ModelType:
        obj_in_data = data.model_dump()
        return await self.model.create(**obj_in_data)

    async def update(self, db_obj: ModelType, data: UpdateSchemaType) -> ModelType:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db_obj.save()
        return db_obj

    async def remove(self, pk: Any) -> int:
        deleted_count = await self.model.filter(pk=pk).delete()
        return deleted_count
