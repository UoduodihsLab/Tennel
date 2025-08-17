# channel/client.py

import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict

from telethon import TelegramClient, types, functions

from app.core.config import settings


class ClientManager:
    def __init__(self, sessions: List[str]):
        self.sessions = sessions
        self.clients: Dict[str, TelegramClient] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def connect_all(self):
        for session in self.sessions:
            client = TelegramClient(session, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

            try:
                await client.connect()
                if not await client.is_user_authorized():
                    print(f'{session} 未授权, 请检查重新登录')
                else:
                    self.clients[session] = client
                    self.locks[session] = asyncio.Lock()
            except Exception as e:
                print(e)

    @asynccontextmanager
    async def get_client(self, session: str):
        if session not in self.locks:
            raise ValueError(f'{session} 客户端不存在或未连接成功')

        lock = self.locks[session]

        await lock.acquire()

        try:
            yield self.clients[session]
        finally:
            lock.release()

    async def disconnect_all(self):
        for client in self.clients.values():
            if client.is_connected():
                await client.disconnect()


def get_static_client_for_phone(phone: str) -> TelegramClient:
    session_file = str(settings.TELEGRAM_SESSIONS_ROOT)
    if settings.ENABLE_PROXY:
        return TelegramClient(session_file, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH, proxy=settings.PROXY)
    return TelegramClient(session_file, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)


async def create_channel(client: TelegramClient, title: str, about: str) -> types.Channel:
    result = await client(
        functions.channels.CreateChannelRequest(
            title=title,
            about=about
        )
    )

    new_channel = result.chats[0]

    return new_channel


async def update_username(client: TelegramClient, tid: int, access_hash: int, username: str) -> bool:
    input_channel = types.InputChannel(tid, access_hash)

    await client(
        functions.channels.UpdateUsernameRequest(
            channel=input_channel,
            username=username
        )
    )

    return True


async def update_photo(client: TelegramClient, tid: int, access_hash: int, photo_path: str) -> bool:
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


async def update_about(client: TelegramClient, tid: int, access_hash: int, about: str) -> bool:
    input_peer_channel = types.InputPeerChannel(tid, access_hash)

    await client(
        functions.messages.EditChatAboutRequest(
            peer=input_peer_channel,
            about=about
        )
    )

    return True
