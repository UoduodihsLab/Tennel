import logging
from tortoise import Tortoise
from .tortoise_config import TORTOISE_ORM

logger = logging.getLogger(__name__)


async def connect_to_db():
    logger.info('正在初始化Tortoise-ORM连接...')
    await Tortoise.init(config=TORTOISE_ORM)
    logger.info('Tortoise-ORM初始化完成')

    
async def close_db_connection():
    logger.info('正在关闭数据库连接...')
    await Tortoise.close_connections()
    logger.info('数据库连接已关闭')