import logging
from typing import List

from fastapi import APIRouter, Depends, status, Query, Request

from app.api.deps import auth_dependency
from app.db.models import UserModel
from app.schemas.channel import ChannelFilter
from app.schemas.common import PageResponse, Pagination
from app.services.channel import ChannelService

logger = logging.getLogger(__name__)

service = ChannelService()

router = APIRouter(
    prefix="/channels",
    tags=["Channel"],
    dependencies=[Depends(auth_dependency)]
)


@router.get(
    "/",
    response_model=PageResponse,
    status_code=status.HTTP_200_OK,
    summary="List channels"
)
async def read_channels(
        request: Request,
        filters: ChannelFilter = Depends(),
        pagination: Pagination = Depends(),
        order_by: List[str] = Query(None, title="Order by", description="Order by")
):
    current_user: UserModel = request.state.user
    filters.user_id = current_user.id
    return await service.list(page=pagination.page, size=pagination.size, filters=filters, order_by=order_by)
