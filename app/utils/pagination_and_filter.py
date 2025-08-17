# utils/pagination.py

from typing import Any, Dict, List, Tuple

from tortoise.queryset import QuerySet


async def paginate_and_filter(
        query: QuerySet,
        filters: Dict[str, Any] | None = None,
        order_by: List[str] | None = None,
        offset: int = 0,
        limit: int = 10,
) -> Tuple[int, List[Any]]:
    if filters:
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        if clean_filters:
            query = query.filter(**clean_filters)

    total = await query.count()

    if order_by:
        query = query.order_by(*order_by)

    rows = await query.offset(offset).limit(limit)

    return total, rows
