import logging
from typing import List

from fastapi import APIRouter, Depends, status, Query, Request, HTTPException
from starlette.responses import JSONResponse

from app.api.deps import auth_dependency
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
    try:
        filters.user_id = request.state.user.id
        return await service.list(page=pagination.page, size=pagination.size, filters=filters, order_by=order_by)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/generate-link/',
    status_code=status.HTTP_201_CREATED,
    summary="Generate link"
)
async def generate_link(request: Request):
    try:
        user_id = request.state.user.id
        await service.generate_link(user_id)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={'msg': 'ok'})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
