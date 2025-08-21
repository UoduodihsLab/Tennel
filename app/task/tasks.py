import logging

from app.constants.enum import AccountRole
from app.core.telegram_client import ClientManager, create_channel
from app.services.channel import ChannelService
from app.services.task import TaskService

logger = logging.getLogger(__name__)


async def process_create_channel(
        user_id: int,
        task_id: int,
        client_manager: ClientManager,
        session_name: str,
        title: str
):
    try:
        async with client_manager.get_client(session_name) as client:
            new_channel = await create_channel(client, title)
            log = f'任务 {task_id} 创建频道成功: {new_channel.id} - {new_channel.title}'
            await TaskService().update_task_status_with_increment_success_and_log(task_id, log)
            await ChannelService().create_channel_with_account(
                user_id,
                new_channel.id,
                new_channel.title,
                new_channel.access_hash,
                AccountRole.OWNER,
                session_name,
            )
    except Exception as e:
        logger.error(f'任务 {task_id} 创建频道失败: {e}')
        log = f'任务 {task_id} 创建频道失败: {title} - {e}'
        await TaskService().update_task_status_with_increment_failure_and_log(task_id, log)


async def process_set_channel_username(
        task_id: int,
        client_manager: ClientManager,
        session_name: str,
        channel_tid: int,
        access_hash: int,
        username: str,
):
    pass


async def process_set_channel_photo(
        task_id: int,
        client_manager: ClientManager,
        session_path: str,
        channel_tid: int,
        access_hash: int,
        photo_url: str,
):
    pass


async def process_set_channel_description(
        task_id: int,
        client_manager: ClientManager,
        session_path: str,
        channel_id: int,
        access_hash: int,
        description: str,
):
    pass
