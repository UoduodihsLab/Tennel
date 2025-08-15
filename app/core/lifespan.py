import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.register import connect_to_db, close_db_connection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('正在启动Tennel...')

    await connect_to_db()

    logger.info('Tennel已启动')

    yield

    await close_db_connection()

    logger.info('Tennel已停止')
