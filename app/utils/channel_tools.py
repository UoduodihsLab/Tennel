import base64
import random
from datetime import datetime, timedelta, timezone
from typing import List

import httpx

from app.core.config import settings


def generate_username_prefix() -> str:
    header_choices = 'abcdefghijklmnopqrstuvwxyz'
    body_choices = 'abcdefghijklmnopqrstuvwxyz0123456789_'
    tail_choices = 'abcdefghijklmnopqrstuvwxyz_'

    header = ''.join(random.sample(header_choices, 2))
    body = ''.join(random.sample(body_choices, 3))
    tail = random.choice(tail_choices)

    return f'{header}{body}{tail}'


def generate_username(channel_tid: int) -> str:
    username_prefix = generate_username_prefix()
    return f'{username_prefix}{channel_tid}'


def generate_random_times(
        num_times: int = 10,
        separation_minutes: int = 30
) -> List[datetime]:
    total_slots = 24 * 60 // separation_minutes
    if num_times > total_slots:
        raise ValueError('无法在满足间隔约束条件下生成所需数量的时间点')

    chosen_slots = random.sample(range(total_slots), num_times)

    now = datetime.now(timezone.utc) + timedelta(hours=8)
    start_time = datetime(now.year, now.month, now.day, 0, 0, tzinfo=timezone.utc) + timedelta(hours=8)

    times = []
    for slot in chosen_slots:
        random_minute_in_slot = random.randint(0, separation_minutes - 1)
        total_minutes = (slot * separation_minutes) + random_minute_in_slot

        hour = total_minutes // 60
        minute = total_minutes % 60
        target_time = start_time + timedelta(hours=hour, minutes=minute)
        times.append(target_time)

    times.sort()
    return times


async def ask_ai(model: str, system_prompt: str, message: str, stream: bool = False):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.AI_API_KEY}'
    }

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': message}
        ],
        'stream': stream
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(settings.AI_API_URL, headers=headers, json=payload, timeout=40)
        response.raise_for_status()

        result = response.json()

        return result['choices'][0]['message']['content']


async def generate_channel_message_to_publish(ai_prompt: str, lang: str, max_word_count: int, min_word_count: int):
    model = 'deepseek-chat'
    sys_prompt = '你是一个虚拟货币领域和营销领域的专家, 你将根据我的需求为我生成可以发在关于虚拟货币类Telegram广播频道的引流文章'
    user_prompt = f'要求如下: 1. 用{lang} 2. {ai_prompt}, 3. {min_word_count}到{max_word_count}字'

    return await ask_ai(model, sys_prompt, user_prompt)


def tid_to_chat_id(tid: int) -> int:
    return int(f'-100{tid}')


def photo_to_base64(photo: bytes) -> str:
    return base64.b64encode(photo).decode()

# if __name__ == '__main__':
#     times = generate_random_times(datetime(2025, 8, 23, 0, 0, 0), 10)
#
#     for t in times:
#         print(str(t))
