import logging
import random
from typing import List

from app.constants.enum import TaskStatus
from app.constants.enum import TaskType
from app.core.config import settings
from app.core.telegram_client import ClientManager
from app.crud.account import AccountCRUD
from app.crud.account_channel import AccountChannelCRUD
from app.crud.channel import ChannelCRUD
from app.crud.task import TaskCRUD
from app.db.models import AccountChannelModel
from app.db.models.task import TaskModel
from app.exceptions import NotFoundRecordError, MuchTooManyChannelsError, UnsupportedTaskTypeError, \
    DeleteRunningTaskError, DuplicateRunningTaskError
from app.schemas.account import AccountOut
from app.schemas.channel import ChannelResponse
from app.schemas.common import PageResponse
from app.schemas.task import TaskFilter, TaskResponse, TaskCreate, BatchCreateChannelArgs, BatchSetChannelUsernameArgs, \
    BatchSetChannelPhotoArgs, BatchSetChannelDescriptionArgs
from app.services.media import MediaService
from app.task.queues import queue_manager
from app.utils.channel_tools import generate_username

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self):
        self.crud = TaskCRUD()

    async def list(self, *, page: int, size: int, filters: TaskFilter, order_by: List[str] | None = None) -> \
            PageResponse[TaskResponse]:
        offset = (page - 1) * size
        filters_dict = filters.model_dump()
        logger.info(filters_dict)
        total, rows = await self.crud.list(
            offset=offset,
            limit=size,
            filters=filters_dict,
            order_by=order_by
        )

        items = [TaskResponse.model_validate(row) for row in rows]

        return PageResponse[TaskResponse](total=total, items=items)

    async def create_channel_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        args = BatchCreateChannelArgs.model_validate(data.args)

        account_id = args.account_id
        total = data.total

        # TODO: 查询是否有相同账号的创建频道的任务, 如果存在则不创建

        account = await AccountCRUD().get(account_id)
        if account is None:
            raise NotFoundRecordError(f'未查询到此账号: {account_id}')

        created_count = await AccountChannelCRUD().count_created_channels(account.id)
        remaining_count = settings.MAX_CHANNELS_COUNT_PER_ACCOUNT - created_count

        if total > remaining_count:
            raise MuchTooManyChannelsError(
                f'请求创建的频道数量超出当前账号剩余可创建频道数量: 当前剩余: {remaining_count}')

        dict_to_create = data.model_dump()
        dict_to_create.update({'user_id': user_id})

        new_task = await self.crud.create(dict_to_create)

        return TaskResponse.model_validate(new_task)

    async def create_set_channel_username_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        args = BatchSetChannelUsernameArgs.model_validate(data.args)

        if data.total != len(args.channel_ids):
            raise ValueError('请求的任务操作总数与实际选中的频道数量不符')

        dict_to_create = data.model_dump()
        dict_to_create.update({'user_id': user_id})
        new_task = await self.crud.create(dict_to_create)

        return TaskResponse.model_validate(new_task)

    async def create_set_channel_photo_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        args = BatchSetChannelPhotoArgs.model_validate(data.args)

        if data.total != len(args.channel_ids):
            raise ValueError('请求任务操作总数与实际选中的频道数量不符')

        dict_to_create = data.model_dump()
        dict_to_create.update({'user_id': user_id})
        new_task = await self.crud.create(dict_to_create)

        return TaskResponse.model_validate(new_task)

    async def create_set_channel_description_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        args = BatchSetChannelDescriptionArgs.model_validate(data.args)
        if data.total != len(args.channel_ids):
            raise ValueError('请求任务操作总数与实际选中的频道数量不符')
        dict_to_create = data.model_dump()
        dict_to_create.update({'user_id': user_id})
        new_task = await self.crud.create(dict_to_create)
        return TaskResponse.model_validate(new_task)

    async def create_task(self, user_id: int, data: TaskCreate) -> TaskResponse:
        t_type = data.t_type

        if t_type == TaskType.CREATE_CHANNEL:
            return await self.create_channel_task(user_id, data)
        if t_type == TaskType.SET_USERNAME:
            return await self.create_set_channel_username_task(user_id, data)
        if t_type == TaskType.SET_PHOTO:
            return await self.create_set_channel_photo_task(user_id, data)
        if t_type == TaskType.SET_DESCRIPTION:
            return await self.create_set_channel_description_task(user_id, data)

        raise UnsupportedTaskTypeError('不支持的任务类型')

    async def start_batch_create_channel(self, task_schema: TaskResponse, client_manager: ClientManager):
        args = task_schema.args
        total = task_schema.total
        titles = args['titles']
        account_id = args.get('account_id')

        account = await AccountCRUD().get(account_id)
        if account is None:
            raise NotFoundRecordError(f'查无此账号: {account_id}')

        session_name = account.session_name
        titles_count = len(titles)
        titles_copy = titles[:]

        for _ in range(total):
            if titles_count >= total:
                title = titles_copy.pop()
            else:
                title = random.choice(titles_copy)

            task_data = (task_schema.id, client_manager, session_name, title)
            queue_manager.create_channel_queue.put_nowait(task_data)

        await self.crud.update(task_schema.id, {'status': TaskStatus.RUNNING})

    async def start_batch_set_channel_username(
            self,
            task_schema: TaskResponse,
            client_manager: ClientManager
    ):
        args = task_schema.args
        channels_to_accounts: List[AccountChannelModel] = []
        channel_ids = args['channel_ids']
        for cid in channel_ids:
            channel_to_account: AccountChannelModel | None = await AccountChannelCRUD().get_with_channel_account(cid)
            if channel_to_account is None:
                raise NotFoundRecordError(f'未查询到此频道相关的记录: {cid}')
            channels_to_accounts.append(channel_to_account)

        for c2a in channels_to_accounts:
            username = generate_username(c2a.channel.tid)
            task_data = (
                task_schema.id,
                client_manager,
                c2a.account.session_name,
                c2a.channel.tid,
                c2a.access_hash,
                username
            )
            queue_manager.set_channel_username_queue.put_nowait(task_data)

        await self.crud.update(task_schema.id, {'status': TaskStatus.RUNNING})

    async def start_batch_set_channel_photo(
            self,
            user_id: int,
            task_schema: TaskResponse,
            client_manager: ClientManager
    ):
        args = task_schema.args
        c2a_list: List[AccountChannelModel] = []
        channel_ids = args['channel_ids']
        for cid in channel_ids:
            c2a: AccountChannelModel | None = await AccountChannelCRUD().get_with_channel_account(cid)
            if c2a is None:
                raise NotFoundRecordError(f'未查询到此频道相关记录: {cid}')

            c2a_list.append(c2a)

        for c2a in c2a_list:
            photo_filename = await MediaService().get_random_avatar_by_user_id(user_id)
            photo_path = str(settings.MEDIA_ROOT / photo_filename)
            task_data = (
                task_schema.id,
                client_manager,
                c2a.account.session_name,
                c2a.channel.tid,
                c2a.access_hash,
                photo_path,
            )
            queue_manager.set_channel_photo_queue.put_nowait(task_data)

        await self.crud.update(task_schema.id, {'status': TaskStatus.RUNNING})

    async def start_batch_set_channel_description(
            self,
            task_schema: TaskResponse,
            client_manager: ClientManager
    ):
        args = task_schema.args
        c2a_list: List[AccountChannelModel] = []
        channel_ids = args['channel_ids']
        for cid in channel_ids:
            c2a: AccountChannelModel | None = await AccountChannelCRUD().get_with_channel_account(cid)
            if c2a is None:
                raise NotFoundRecordError(f'未查询到此频道相关记录: {cid}')
            c2a_list.append(c2a)

        for c2a in c2a_list:
            description = args['description']
            task_data = (
                task_schema.id,
                client_manager,
                c2a.account.session_name,
                c2a.channel.tid,
                c2a.access_hash,
                description,
            )
            queue_manager.set_channel_description_queue.put_nowait(task_data)

        await self.crud.update(task_schema.id, {'status': TaskStatus.RUNNING})

    async def start_task(self, task_id: int, user_id: int, client_manager: ClientManager):
        # TODO: 有待优化，这一步是判断任务是否存在兼任务是否属于当前用户
        task = await self.crud.get_with_user_id(task_id, user_id)
        if task is None:
            raise NotFoundRecordError(f'任务 {task_id} 不存在')

        if task.status != TaskStatus.PENDING:
            raise DuplicateRunningTaskError('不可重复运行同一个任务')

        task_schema = TaskResponse.model_validate(task)
        task_type = task_schema.t_type
        if task_type == TaskType.CREATE_CHANNEL:
            return await self.start_batch_create_channel(task_schema, client_manager)

        if task_type == TaskType.SET_USERNAME:
            return await self.start_batch_set_channel_username(task_schema, client_manager)

        if task_type == TaskType.SET_PHOTO:
            return await self.start_batch_set_channel_photo(user_id, task_schema, client_manager)

        if task_type == TaskType.SET_DESCRIPTION:
            return await self.start_batch_set_channel_description(task_schema, client_manager)

        raise UnsupportedTaskTypeError('不支持的任务类型')

    async def delete_task(self, task_id: int, user_id: int):
        task = await self.crud.get_with_user_id(task_id, user_id)

        if task is None:
            raise NotFoundRecordError(f'查无此任务: {task_id}')

        if task.status == TaskStatus.RUNNING:
            raise DeleteRunningTaskError('当前任务正在运行, 请等待任务运行完毕后重试')

        await self.crud.delete(task_id)

    async def update_task_status_with_increment_success_and_log(self, task_id: int, log: str):
        await self.crud.increment_success(task_id)
        await self.crud.append_log(task_id, log)

        task: TaskModel | None = await self.crud.get(task_id)
        if task.success + task.failure == task.total:
            await self.crud.update(task_id, {'status': TaskStatus.COMPLETED})

    async def update_task_status_with_increment_failure_and_log(self, task_id: int, log: str):
        await self.crud.increment_failure(task_id)
        await self.crud.append_log(task_id, log)
        task: TaskModel | None = await self.crud.get(task_id)
        if task.success + task.failure == task.total:
            await self.crud.update(task_id, {'status': TaskStatus.COMPLETED})

    @staticmethod
    async def get_available_channels(user_id: int) -> List[ChannelResponse]:
        rows = await ChannelCRUD().filter_by_user_id(user_id)
        return [ChannelResponse.model_validate(row) for row in rows]

    @staticmethod
    async def get_available_accounts(user_id: int) -> List[AccountOut]:
        rows = await AccountCRUD().list_online_by_user_id(user_id)

        available_accounts = [
            row for row in rows
            if await AccountChannelCRUD().count_created_channels(row.id) < settings.MAX_CHANNELS_COUNT_PER_ACCOUNT
        ]
        return [AccountOut.model_validate(item) for item in available_accounts]
