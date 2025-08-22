from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.constants.enum import ScheduleType
from app.core.telegram_client import ClientManager
from app.crud.schedule import ScheduleCRUD
from app.db.models.schedule import ScheduleModel
from app.exceptions import UnsupportedSchedulerTypeError, NotFoundRecordError
from app.schemas.common import PageResponse
from app.schemas.schedule import ScheduleIn, ScheduleOut, ScheduleFilter, PublishMessageArgs
from app.task.schedules import create_daily_publish_message_scheduler


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

    async def create_publish_message_schedule(self, user_id: int, data: ScheduleIn) -> ScheduleOut:
        PublishMessageArgs.model_validate(data.args)

        # TODO: 检查包含的频道是否已被其他定时任务绑定, 以及频道是否属于当前用户

        dict_to_create = ScheduleIn.model_dump(data)
        dict_to_create.update({'user_id': user_id})

        new_scheduler = await self.crud.create(dict_to_create)
        return ScheduleOut.model_validate(new_scheduler)

    async def create_schedule(self, user_id: int, data: ScheduleIn):
        if data.s_type == ScheduleType.PUBLISH_MESSAGE:
            return await self.create_publish_message_schedule(user_id, data)

        raise UnsupportedSchedulerTypeError('不支持的定时任务类型')

    async def start_schedule(
            self,
            schedule_id: int,
            user_id: int,
            scheduler: AsyncIOScheduler,
            client_manager: ClientManager
    ) -> bool:
        schedule_record: ScheduleModel | None = await self.crud.get_join_user_id(schedule_id, user_id)

        if schedule_record is None:
            raise NotFoundRecordError(f'查无此定时任务 {schedule_id}')

        if schedule_record.s_type == ScheduleType.PUBLISH_MESSAGE:
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
                id=f'publish_message_main_{schedule_record.id}'
            )

            return True

        raise UnsupportedSchedulerTypeError('不支持的定时任务类型')
