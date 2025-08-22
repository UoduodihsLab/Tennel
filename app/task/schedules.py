import logging
from typing import List
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.telegram_client import ClientManager
from app.core.telegram_client import send_message_to_channel, send_file_to_channel
from app.crud.account_channel import AccountChannelCRUD
from app.db.models import AccountChannelModel
from app.services.media import MediaService
from app.utils.channel_tools import generate_random_times, generate_channel_message_to_publish, tid_to_chat_id

logger = logging.getLogger(__name__)


async def process_publish_message(
        user_id: int,
        client_manager: ClientManager,
        tid: int,
        lang: str,
        session_name: str,
        min_word_count: int,
        max_word_count: int,
        include_imgs: bool,
        include_videos: bool,
        include_primary_links: bool,
        primary_links: str,
        ai_prompt,
):
    message_text = await generate_channel_message_to_publish(ai_prompt, lang, min_word_count, max_word_count)

    media_list = []
    if include_imgs:
        img = await MediaService().get_random_img_by_user_id(user_id)
        img_path = str(settings.MEDIA_ROOT / img)
        media_list.append(img_path)

    if include_videos:
        video = await MediaService().get_random_video_by_user_id(user_id)
        video_path = str(settings.MEDIA_ROOT / video)
        media_list.append(video_path)

    if include_primary_links:
        message_text += f'\nSubscribe us: {primary_links}'

    async with client_manager.get_client(session_name) as client:
        chat_id = tid_to_chat_id(tid)
        if media_list:
            await send_file_to_channel(client, chat_id, media_list, message_text)
            logger.info(f'{tid} - {media_list} - {message_text} successfully sent')
        else:
            await send_message_to_channel(client, chat_id, message_text)
            logger.info(f'{tid} - {media_list} - {message_text} successfully sent')


async def create_daily_publish_message_scheduler(
        scheduler: AsyncIOScheduler,
        client_manager: ClientManager,
        user_id: int,
        min_word_count: int,
        max_word_count: int,
        include_imgs: bool,
        include_videos: bool,
        include_primary_links: bool,
        ai_prompt: str,
        channels_ids: List[str],
):
    try:
        for cid in channels_ids:
            c2a: AccountChannelModel | None = await AccountChannelCRUD().get_with_channel_account(cid)
            times = generate_random_times()
            primary_links = ','.join(c2a.channel.primary_links)
            for t in times:
                scheduler.add_job(
                    func=process_publish_message,
                    trigger='date',
                    run_date=t,
                    args=[
                        user_id,
                        client_manager,
                        c2a.channel.tid,
                        c2a.channel.lang,
                        c2a.account.session_name,
                        min_word_count,
                        max_word_count,
                        include_imgs,
                        include_videos,
                        include_primary_links,
                        primary_links,
                        ai_prompt,
                    ],
                    id=str(uuid4()),
                    replace_existing=True,
                )
    except Exception as e:
        logger.error(e)
