import random


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
