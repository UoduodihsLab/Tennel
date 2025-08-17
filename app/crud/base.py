# crud/base.py

from typing import Type, TypeVar, Generic, Dict, Any, List

from tortoise.models import Model

from app.utils.pagination_and_filter import paginate_and_filter

ModelType = TypeVar('ModelType', bound=Model)


class BaseCRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, pk: Any) -> ModelType | None:
        return await self.model.filter(pk=pk).first()

    async def create(self, data: Dict[str, Any]) -> ModelType:
        return await self.model(**data)

    async def update(self, db_obj: ModelType, data: Dict[str, Any]) -> ModelType:
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db_obj.save()
        return db_obj

    async def delete(self, pk: Any) -> int:
        return await self.model.filter(pk=pk).delete()

    async def list_filtered(
            self,
            offset: int = 0,
            limit: int = 10,
            filters: Dict[str, Any] = None,
            order_by: List[str] = None,
    ):
        query = self.model.all()

        total, rows = await paginate_and_filter(query, filters, order_by, offset, limit)

        return total, rows
