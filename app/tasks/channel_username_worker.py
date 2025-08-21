import asyncio
import logging
from app.tclient.client import ClientManager


logger = logging.getLogger(__name__)


async def channel_username_worker(name: str, queue: asyncio.Queue):
    while True:
        try:
            args = await queue.get()
            session_name = args.get('session_name')
        except asyncio.CancelledError:
            logger.error(f"Worker {name} 被关闭")
            break