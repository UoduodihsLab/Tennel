import logging
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.constants.enum import ScheduleStatus
from app.core.telegram_client import ClientManager
from app.crud.channel import ChannelCRUD
from app.crud.schedule import ScheduleCRUD
from app.db.models.schedule import ScheduleModel
from app.exceptions import NotFoundRecordError
from app.schemas.channel import ChannelResponse
from app.schemas.common import PageResponse
from app.schemas.schedule import ScheduleIn, ScheduleOut, ScheduleFilter, PublishMessageArgs
from app.task.schedules import create_daily_publish_message_scheduler

logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self):
        self.crud = ScheduleCRUD()

    async def list(
            self,
            page: int,
            size: int,
            filters: ScheduleFilter,
            order_by: List[str]
    ) -> PageResponse[ScheduleOut]:
        offset = (page - 1) * size
        filters_dict = ScheduleFilter.model_dump(filters)
        total, rows = await self.crud.list(offset=offset, limit=size, filters=filters_dict, order_by=order_by)
        items = [ScheduleOut.model_validate(row) for row in rows]
        return PageResponse[ScheduleOut](total=total, items=items)

    async def create_schedule(self, user_id: int, data: ScheduleIn):
        PublishMessageArgs.model_validate(data.args)

        # TODO: 检查包含的频道是否已被其他定时任务绑定, 以及频道是否属于当前用户

        dict_to_create = ScheduleIn.model_dump(data)
        dict_to_create.update({'user_id': user_id})
        new_scheduler = await self.crud.create(dict_to_create)

        return ScheduleOut.model_validate(new_scheduler)

    async def start_schedule(
            self,
            user_id: int,
            schedule_id: int,
            scheduler: AsyncIOScheduler,
            client_manager: ClientManager
    ) -> int:
        logger.info(f'current_user_id: {user_id}')
        schedule_record: ScheduleModel | None = await self.crud.get_join_user_id(schedule_id, user_id)

        if schedule_record is None:
            raise NotFoundRecordError(f'查无此定时任务 {schedule_id}')

        job_id = f'{schedule_record.id}'
        job = scheduler.get_job(job_id)

        if job is not None:
            scheduler.resume_job(job_id)
        else:
            scheduler.add_job(
                func=create_daily_publish_message_scheduler,
                trigger='cron',
                hour=schedule_record.hour,
                minute=schedule_record.minute,
                second=schedule_record.second,
                kwargs={
                    'scheduler': scheduler,
                    'client_manager': client_manager,
                    'user_id': user_id,
                    **schedule_record.args
                },
                id=f'{schedule_record.id}'
            )
        await self.crud.update(schedule_record.id, {'status': ScheduleStatus.RUNNING})
        return schedule_record.id

    async def stop_schedule(self, user_id: int, schedule_id: int, scheduler: AsyncIOScheduler) -> int:
        schedule_record: ScheduleModel | None = await self.crud.get_join_user_id(schedule_id, user_id)
        if schedule_record is None:
            raise NotFoundRecordError(f'查无此定时任务 {schedule_id}')

        job_id = f'{schedule_record.id}'
        job = scheduler.get_job(job_id)
        if job is not None:
            scheduler.pause_job(job_id)
        await self.crud.update(schedule_record.id, {'status': ScheduleStatus.PENDING})
        return schedule_record.id

    async def delete_schedule(self, user_id: int, schedule_id: int, scheduler: AsyncIOScheduler) -> bool:
        schedule_record: ScheduleModel | None = await self.crud.get_join_user_id(schedule_id, user_id)
        if schedule_record is None:
            raise NotFoundRecordError(f'查无此任务 {schedule_id}')

        job_id = f'{schedule_record.id}'
        job = scheduler.get_job(job_id)
        if job is not None:
            scheduler.pause_job(job_id)
            scheduler.remove_job(job_id)
        await self.crud.delete(schedule_record.id)
        return schedule_record.id

    async def get_available_channels(self, user_id: int) -> List[ChannelResponse]:
        channels = await ChannelCRUD().filter_by_user_id(user_id)
        schedules = await self.crud.filter_by_user_id(user_id)
        included_ids = [cid for item in schedules for cid in item.args['channels_ids']]

        available_channels = []
        for channel in channels:
            if channel.id in included_ids:
                continue
            available_channels.append(ChannelResponse.model_validate(channel))
        return available_channels
