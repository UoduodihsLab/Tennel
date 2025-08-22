import logging
from typing import List

from fastapi import APIRouter, File, UploadFile, Depends, status, Request, HTTPException, Query, Form

from app.api.deps import auth_dependency
from app.constants.enum import MediaType
from app.db.models.user import UserModel
from app.schemas.common import PageResponse, Pagination
from app.schemas.media import MediaResponse, MediaFilter
from app.services.media import MediaService

logger = logging.getLogger(__name__)

service = MediaService()

router = APIRouter(
    prefix="/medias",
    tags=["Medias"],
    dependencies=[Depends(auth_dependency)]
)


@router.post(
    '/',
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new media file"
)
async def create_media(request: Request, m_type: MediaType = Form(...), file: UploadFile = File(...)):
    current_user: UserModel = request.state.user
    try:
        return await service.create_media(current_user.id, file, m_type)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    '/',
    response_model=PageResponse[MediaResponse],
    status_code=status.HTTP_200_OK,
    summary="List media files"
)
async def read_medias(
        request: Request,
        pagination: Pagination = Depends(),
        filters: MediaFilter = Depends(),
        order_by: List[str] = Query(None)
):
    current_user: UserModel = request.state.user
    filters.user_id = current_user.id
    try:
        return await service.list(pagination.page, pagination.size, filters, order_by)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
