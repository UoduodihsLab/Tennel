# channel/client.py

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Tuple

from telethon import TelegramClient, types, functions

from app.core.config import settings

logger = logging.getLogger(__name__)


class ClientManager:
    def __init__(
            self,
            *,
            api_id: int,
            api_hash: str,
            enable_proxy: bool,
            proxy: Tuple[str, str, int, str, str],
            sessions_root: str,
            # sessions: List[str],
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.enable_proxy = enable_proxy
        self.proxy = proxy
        self.sessions_root = sessions_root
        # self.sessions = sessions

        self.clients: Dict[str, TelegramClient] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

        self._manager_lock = asyncio.Lock()

    async def connect_client(self, session_name: str) -> bool:
        session_path = f'{self.sessions_root}/{session_name}'

        proxy_info = self.proxy if self.enable_proxy else None

        client = TelegramClient(session_path, self.api_id, self.api_hash, proxy=proxy_info)

        try:
            logger.info(f'正在连接 {session_name} ...')
            await client.connect()
            if not await client.is_user_authorized():
                logger.info(f'{session_name} 未授权, 请检查或重新登录')
                await client.disconnect()
                return False

            async with self._manager_lock:
                self.clients[session_name] = client
                self.locks[session_name] = asyncio.Lock()

            logger.info(f'{session_name} 连接成功.')
            return True
        except Exception as e:
            logger.error(f'连接 {session_name} 时发生错误: {e}')
            return False

    # async def connect_all(self):
    #     tasks = [self.connect_client(session) for session in self.sessions]
    #     await asyncio.gather(*tasks)

    async def is_online(self, session_name: str) -> bool:
        async with self._manager_lock:
            return session_name in self.clients

    @asynccontextmanager
    async def get_client(self, session_name: str):
        async with self._manager_lock:
            if session_name not in self.locks:
                raise ValueError(f'{session_name} 客户端不存在或未连接成功')

            lock = self.locks[session_name]
            client = self.clients[session_name]

        await lock.acquire()
        try:
            yield client
        finally:
            lock.release()

    async def remove_client(self, session_name: str):
        client_to_remove = None
        lock_to_wait_on = None

        async with self._manager_lock:
            if session_name in self.clients:
                client_to_remove = self.clients.pop(session_name)
                lock_to_wait_on = self.locks.pop(session_name)
                logger.info(f'客户端 {session_name} 已从管理器中移除, 等待其他任务完成...')
            else:
                logger.warning(f'尝试移除不存在的客户端 {session_name}')
                return

        if client_to_remove and lock_to_wait_on:
            async with lock_to_wait_on:
                logger.info(f'客户端 {session_name} 的所有任务已完成, 准备断开连接...')
                if client_to_remove.is_connected():
                    await client_to_remove.disconnect()
                logger.info(f'客户端 {session_name} 已成功断开连接并移除.')

    async def disconnect_all(self):
        logger.info('准备断开所有客户端连接...')
        all_clients_to_disconnect = []
        async with self._manager_lock:
            all_clients_to_disconnect = list(self.clients.values())
            self.clients.clear()
            self.locks.clear()

        tasks = [client.disconnect() for client in all_clients_to_disconnect if client.is_connected()]
        await asyncio.gather(*tasks)
        logger.info('所有客户端已断开连接')


async def setup_client_manager() -> ClientManager:
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    enable_proxy = settings.ENABLE_PROXY
    proxy = settings.PROXY
    sessions_root = settings.TELEGRAM_SESSIONS_ROOT
    # sessions_name = await AccountCRUD().list_authenticated_only_session_name()

    client_manager = ClientManager(
        api_id=api_id,
        api_hash=api_hash,
        enable_proxy=enable_proxy,
        proxy=proxy,
        sessions_root=sessions_root,
        # sessions=sessions_name,
    )

    # await client_manager.connect_all()

    return client_manager


def get_static_client_for_phone(phone: str) -> TelegramClient:
    session_file = str(settings.TELEGRAM_SESSIONS_ROOT / phone)
    if settings.ENABLE_PROXY:
        return TelegramClient(session_file, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH,
                              proxy=settings.PROXY)
    return TelegramClient(session_file, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)


async def create_channel(client: TelegramClient, title: str, about: str = '') -> types.Channel:
    result = await client(
        functions.channels.CreateChannelRequest(
            title=title,
            about=about
        )
    )

    new_channel = result.chats[0]

    return new_channel


async def set_channel_username(client: TelegramClient, tid: int, access_hash: int, username: str) -> bool:
    input_channel = types.InputChannel(tid, access_hash)

    await client(
        functions.channels.UpdateUsernameRequest(
            channel=input_channel,
            username=username
        )
    )

    return True


async def set_channel_photo(client: TelegramClient, tid: int, access_hash: int, photo_path: str) -> bool:
    input_channel = types.InputChannel(tid, access_hash)
    uploaded_photo = await client.upload_file(photo_path)
    chat_upload_photo = types.InputChatUploadedPhoto(uploaded_photo)

    await client(
        functions.channels.EditPhotoRequest(
            channel=input_channel,
            photo=chat_upload_photo
        )
    )

    return True


async def set_channel_description(client: TelegramClient, tid: int, access_hash: int, about: str) -> bool:
    input_peer_channel = types.InputPeerChannel(tid, access_hash)

    await client(
        functions.messages.EditChatAboutRequest(
            peer=input_peer_channel,
            about=about
        )
    )

    return True


async def send_message_to_channel(client: TelegramClient, tid: int, message: str):
    await client.send_message(tid, message)


async def send_file_to_channel(client: TelegramClient, tid: int, media_list: List[str], caption: str):
    await client.send_file(tid, file=media_list, caption=caption)


async def fetch_latest_channels(client: TelegramClient) -> List[types.Channel]:
    dialogs = await client.get_dialogs()

    channels = []
    for dialog in dialogs:
        entity = dialog.entity
        if isinstance(entity, types.Channel) and entity.broadcast and entity.admin_rights:
            channels.append(entity)

    return channels
