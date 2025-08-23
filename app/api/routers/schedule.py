import logging
import traceback
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import APIRouter, Depends, status, Request, HTTPException, Query
from starlette.responses import JSONResponse

from app.api.deps import auth_dependency, get_scheduler, get_client_manager
from app.core.telegram_client import ClientManager
from app.db.models.user import UserModel
from app.schemas.common import PageResponse, Pagination
from app.schemas.schedule import ScheduleOut, ScheduleFilter, ScheduleIn
from app.services.schedule import ScheduleService

service = ScheduleService()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/schedules",
    tags=["Schedule"],
    dependencies=[Depends(auth_dependency)],
)


@router.post(
    '/',
    response_model=ScheduleOut,
    status_code=status.HTTP_201_CREATED,
    summary='Create new schedule',
)
async def create_schedule(request: Request, data: ScheduleIn):
    try:
        current_user: UserModel = request.state.user
        return await service.create_schedule(current_user.id, data)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/{schedule_id}/start/',
    status_code=status.HTTP_200_OK,
    summary='Start schedule',
)
async def start_schedule(
        request: Request,
        schedule_id: int,
        scheduler: AsyncIOScheduler = Depends(get_scheduler),
        client_manager: ClientManager = Depends(get_client_manager)
):
    try:
        current_user: UserModel = request.state.user
        await service.start_schedule(current_user.id, schedule_id, scheduler, client_manager)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'schedule_id': schedule_id})
    except Exception as e:
        logger.error(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/{schedule_id}/stop/',
    status_code=status.HTTP_200_OK,
    summary='Stop schedule',
)
async def stop_schedule(request: Request, schedule_id: int, scheduler: AsyncIOScheduler = Depends(get_scheduler)):
    try:
        current_user: UserModel = request.state.user
        await service.stop_schedule(current_user.id, schedule_id, scheduler)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'schedule_id': schedule_id})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    '/{schedule_id}/resume/',
    status_code=status.HTTP_200_OK,
    summary='Resume schedule',
)
async def resume_schedule(
        request: Request,
        schedule_id: int,
        scheduler: AsyncIOScheduler = Depends(get_scheduler),
        client_manager: ClientManager = Depends(get_client_manager)
):
    try:
        current_user: UserModel = request.state.user
        await service.start_schedule(current_user.id, schedule_id, scheduler, client_manager)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'schedule_id': schedule_id})
    except Exception as e:
        logger.error(e)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    '/{schedule_id}/',
    status_code=status.HTTP_200_OK,
    summary='Delete schedule'
)
async def delete_schedule(request: Request, schedule_id: int, scheduler: AsyncIOScheduler = Depends(get_scheduler)):
    try:
        current_user: UserModel = request.state.user
        await service.delete_schedule(current_user.id, schedule_id, scheduler)
        return JSONResponse(status_code=status.HTTP_200_OK, content={'schedule_id': schedule_id})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    '/',
    response_model=PageResponse[ScheduleOut],
    status_code=status.HTTP_200_OK,
    summary="Get schedules",
)
async def read_schedules(
        pagination: Pagination = Depends(),
        filters: ScheduleFilter = Depends(),
        order_by: List[str] = Query(None, title="Ordering by")
):
    try:
        return await service.list(pagination.page, pagination.size, filters, order_by)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
