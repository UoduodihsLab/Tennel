import logging
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.db.register import connect_to_db, close_db_connection
from .telegram_client import setup_client_manager
from app.task.workers import create_channel_worker, set_channel_username_worker, set_channel_photo_worker, \
    set_channel_description_worker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('正在启动Tennel...')

    await connect_to_db()

    client_manager = await setup_client_manager()
    app.state.client_manager = client_manager

    asyncio.create_task(create_channel_worker())
    asyncio.create_task(set_channel_username_worker())
    asyncio.create_task(set_channel_photo_worker())
    asyncio.create_task(set_channel_description_worker())


    logger.info('Tennel已启动')

    yield

    await app.state.client_manager.disconnect_all()

    await close_db_connection()

    logger.info('Tennel已停止')
