import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.scheduler import setup_scheduler
from app.db.register import connect_to_db, close_db_connection
from app.task.workers import (
    create_channel_worker,
    set_channel_username_worker,
    set_channel_photo_worker,
    set_channel_description_worker
)
from .status_sync import launch_accounts, stop_schedules, unlaunch_accounts, stop_tasks
from .system_schedules import add_system_schedules
from .telegram_client import setup_client_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('正在启动Tennel...')

    await connect_to_db()

    client_manager = await setup_client_manager()

    await launch_accounts(client_manager)

    scheduler = setup_scheduler()
    logger.info('正在启动定时任务管理器...')
    scheduler.start()

    await add_system_schedules(scheduler, client_manager)

    asyncio.create_task(create_channel_worker())
    asyncio.create_task(set_channel_username_worker())
    asyncio.create_task(set_channel_photo_worker())
    asyncio.create_task(set_channel_description_worker())

    app.state.client_manager = client_manager
    app.state.scheduler = scheduler

    logger.info('Tennel已启动')

    yield

    await stop_schedules(app.state.scheduler)
    await unlaunch_accounts(app.state.client_manager)
    await stop_tasks()

    logger.info('正在关闭定时任务管理器...')
    app.state.scheduler.shutdown()

    await close_db_connection()

    logger.info('Tennel已停止')
