import os
import random
from pathlib import Path
from typing import List

import magic
from fastapi import UploadFile

from app.constants.enum import MediaType
from app.core.config import settings
from app.crud.media import MediaCRUD
from app.exceptions import UnsupportedMediaTypeError, MediaTooLargeError, NotFoundRecordError
from app.schemas.common import PageResponse
from app.schemas.media import MediaFilter, MediaOut
from app.utils.media_tools import generate_filename, save_file_async


class MediaService:
    def __init__(self):
        self.crud = MediaCRUD()

    async def list(
            self,
            page: int,
            size: int,
            filters: MediaFilter,
            order_by: List[str] | None = None,
    ) -> PageResponse[MediaOut]:
        offset = (page - 1) * size
        filters_dict = filters.model_dump()

        total, rows = await self.crud.list(
            offset=offset,
            limit=size,
            filters=filters_dict,
            order_by=order_by,
        )

        items = [MediaOut.model_validate(row) for row in rows]

        return PageResponse[MediaOut](total=total, items=items)

    async def create_avatar(self, user_id: int, file: UploadFile) -> MediaOut:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()

        if file_size > settings.IMG_MAX_SIZE:
            raise MediaTooLargeError('仅允许上传最大15M的图片')

        await file.seek(0)

        contents = await file.read(2048)
        await file.seek(0)

        detected_mime_type = magic.from_buffer(contents, mime=True)
        if detected_mime_type not in settings.ALLOWED_IMAGE_TYPES:
            raise UnsupportedMediaTypeError('不支持的此格式的图片')

        file_ext = Path(file.filename).suffix
        safe_filename = f'{generate_filename()}{file_ext}'
        save_path = settings.MEDIA_ROOT / safe_filename

        await save_file_async(file, save_path)

        created_avatar = await self.crud.create(
            {
                'user_id': user_id,
                'filename': safe_filename,
                'm_type': MediaType.AVATAR
            }
        )

        return MediaOut.model_validate(created_avatar)

    async def create_image(self, user_id: int, file: UploadFile) -> MediaOut:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()

        if file_size > settings.IMG_MAX_SIZE:
            raise MediaTooLargeError('仅允许上传最大15M的图片')

        await file.seek(0)

        contents = await file.read(2048)
        await file.seek(0)

        detected_mime_type = magic.from_buffer(contents, mime=True)
        if detected_mime_type not in settings.ALLOWED_IMAGE_TYPES:
            raise UnsupportedMediaTypeError('不支持的此格式的图片')

        file_ext = Path(file.filename).suffix
        safe_filename = f'{generate_filename()}{file_ext}'
        save_path = settings.MEDIA_ROOT / safe_filename

        await save_file_async(file, save_path)

        created_avatar = await self.crud.create(
            {
                'user_id': user_id,
                'filename': safe_filename,
                'm_type': MediaType.IMAGE
            }
        )

        return MediaOut.model_validate(created_avatar)

    async def create_video(self, user_id: int, file: UploadFile) -> MediaOut:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()

        if file_size > settings.VIDEO_MAX_SIZE:
            raise MediaTooLargeError('仅允许上传最大100M的图片')

        await file.seek(0)

        contents = await file.read(2048)
        await file.seek(0)

        detected_mime_type = magic.from_buffer(contents, mime=True)
        if detected_mime_type not in settings.ALLOWED_VIDEO_TYPES:
            raise UnsupportedMediaTypeError('不支持的此格式的视频')

        file_ext = Path(file.filename).suffix
        safe_filename = f'{generate_filename()}{file_ext}'
        save_path = settings.MEDIA_ROOT / safe_filename

        await save_file_async(file, save_path)

        created_avatar = await self.crud.create(
            {
                'user_id': user_id,
                'filename': safe_filename,
                'm_type': MediaType.VIDEO
            }
        )

        return MediaOut.model_validate(created_avatar)

    async def create_media(self, user_id: int, file: UploadFile, m_type: MediaType) -> MediaOut:
        if m_type == MediaType.AVATAR:
            return await self.create_avatar(user_id, file)
        if m_type == MediaType.IMAGE:
            return await self.create_image(user_id, file)
        if m_type == MediaType.VIDEO:
            return await self.create_video(user_id, file)

        raise UnsupportedMediaTypeError('不支持的媒体类型')

    async def get_random_avatar_by_user_id(self, user_id: int):
        paths_list = await self.crud.get_medias_by_user_id_and_m_type(user_id, MediaType.AVATAR)

        if len(paths_list) == 0:
            raise NotFoundRecordError('未找到头像资源, 请先上传头像后再试')

        return random.choice(paths_list)

    async def get_random_img_by_user_id(self, user_id: int) -> str:
        paths_list = await self.crud.get_medias_by_user_id_and_m_type(user_id, MediaType.IMAGE)

        if len(paths_list) == 0:
            raise NotFoundRecordError('未找到图片资源, 请先上传图片后再试')

        return random.choice(paths_list)

    async def get_random_video_by_user_id(self, user_id: int) -> str:
        paths_list = await self.crud.get_medias_by_user_id_and_m_type(user_id, MediaType.VIDEO)

        if len(paths_list) == 0:
            raise NotFoundRecordError('未找到视频资源, 请先上传视频后再试')

        return random.choice(paths_list)
