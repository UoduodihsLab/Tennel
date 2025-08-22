import asyncio
import logging

from .queues import queue_manager
from .tasks import process_create_channel, process_set_channel_username, process_set_channel_photo, \
    process_set_channel_description

logger = logging.getLogger(__name__)


async def create_channel_worker():
    logger.info('正在初始化 create_channel_worker...')
    while True:
        try:
            task_data = await queue_manager.create_channel_queue.get()
            await process_create_channel(*task_data)
            queue_manager.create_channel_queue.task_done()
        except Exception as e:
            logger.error(f'Failed to create channel worker: {e}')
            queue_manager.create_channel_queue.task_done()
            await asyncio.sleep(1)


async def set_channel_username_worker():
    logger.info('正在初始化 set_channel_username_worker...')
    while True:
        try:
            task_data = await queue_manager.set_channel_username_queue.get()
            await process_set_channel_username(*task_data)
            queue_manager.set_channel_username_queue.task_done()
        except Exception as e:
            logger.error(f'Failed to set channel username worker: {e}')
            queue_manager.set_channel_username_queue.task_done()
            await asyncio.sleep(1)


async def set_channel_photo_worker():
    logger.info('正在初始化 set_channel_photo_worker...')
    while True:
        try:
            task_data = await queue_manager.set_channel_photo_queue.get()
            await process_set_channel_photo(*task_data)
            queue_manager.set_channel_photo_queue.task_done()
        except Exception as e:
            logger.error(f'Failed to set channel photo worker: {e}')
            queue_manager.set_channel_photo_queue.task_done()
            await asyncio.sleep(1)


async def set_channel_description_worker():
    logger.info('正在初始化 set_channel_description_worker...')
    while True:
        try:
            task_data = await queue_manager.set_channel_description_queue.get()
            await process_set_channel_description(*task_data)
            queue_manager.set_channel_description_queue.task_done()
        except Exception as e:
            logger.error(f'Failed to set channel description worker: {e}')
            queue_manager.set_channel_description_queue.task_done()
            await asyncio.sleep(1)
