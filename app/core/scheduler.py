from apscheduler.schedulers.asyncio import AsyncIOScheduler

import logging

logger = logging.getLogger(__name__)


def setup_scheduler() -> AsyncIOScheduler:
    logger.info('正在初始化定时任务调度器...')
    scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
    logger.info('定时任务调度器初始化成功')
    return scheduler
