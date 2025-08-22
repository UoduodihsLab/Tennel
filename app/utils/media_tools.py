from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile


def generate_filename():
    return str(uuid4())


async def save_file_async(file: UploadFile, save_path: Path):
    chunk_size = 1024 * 1024

    try:
        async with aiofiles.open(save_path, mode='wb') as buffer:
            while chunk := await file.read(chunk_size):
                await buffer.write(chunk)

    finally:
        await file.close()
