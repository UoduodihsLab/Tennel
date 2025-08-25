import logging
import traceback
from typing import Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import types, TelegramClient
from tortoise.transactions import in_transaction

from app.constants.enum import AccountRole
from app.core.telegram_client import ClientManager, fetch_latest_channels
from app.crud.account import AccountCRUD
from app.crud.account_channel import AccountChannelCRUD
from app.crud.channel import ChannelCRUD
from app.db.models import AccountModel
from app.utils.channel_tools import photo_to_base64

logger = logging.getLogger(__name__)


async def sync_channels_to_db(channels: List[types.Channel], user_id: int, client: TelegramClient, account_id: int):
    for channel in channels:
        data: Dict[str, Any] = {'user_id': user_id, 'title': channel.title}
        if channel.username:
            data.update({'username': channel.username})

        if isinstance(channel.photo, types.ChatPhoto):
            photo = await client.download_profile_photo(channel, file=bytes)
            photo_base64 = photo_to_base64(photo)
            data.update({'photo': photo_base64})

        async with in_transaction():
            created, updated = await ChannelCRUD().create_or_update_by_tid(channel.id, data)
            if created:
                c2a_data = {
                    'account_id': account_id,
                    'channel_id': created.id,
                    'access_hash': channel.access_hash,
                    'role': AccountRole.ADMIN,
                }
                await AccountChannelCRUD().create(c2a_data)


async def process_sync_channels(client_manager: ClientManager):
    try:
        online_accounts: List[AccountModel] = await AccountCRUD().list_online()
        for account in online_accounts:
            async with client_manager.get_client(account.session_name) as client:
                latest_channels = await fetch_latest_channels(client)
                await sync_channels_to_db(latest_channels, account.user.id, client, account.id)
    except Exception as e:
        traceback.print_exc()
        logger.error(e)


async def add_sync_channels_schedule(scheduler: AsyncIOScheduler, client_manager: ClientManager):
    job_id = 'sync_channels'
    scheduler.add_job(
        func=process_sync_channels,
        trigger='interval',
        args=[client_manager],
        minutes=1,
        id=job_id,
    )


async def sync_accounts_online_status(client_manager: ClientManager):
    try:
        authenticated_accounts: List[AccountModel] = await AccountCRUD().list_authenticated()
        for account in authenticated_accounts:
            if await client_manager.is_online(account.session_name):
                await AccountCRUD().update(account.id, {'online': True})
            else:
                await AccountCRUD().update(account.id, {'online': False})
    except Exception as e:
        logger.error(e)


async def add_sync_accounts_online_status_schedule(scheduler: AsyncIOScheduler, client_manager: ClientManager):
    job_id = 'sync_accounts_online_status'
    scheduler.add_job(
        func=sync_accounts_online_status,
        trigger='interval',
        args=[client_manager],
        seconds=2,
        id=job_id
    )


async def add_system_schedules(scheduler: AsyncIOScheduler, client_manager: ClientManager):
    await add_sync_channels_schedule(scheduler, client_manager)
    await add_sync_accounts_online_status_schedule(scheduler, client_manager)
