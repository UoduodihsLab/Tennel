# app/db/tortoise_config.py

from app.core.config import settings

TORTOISE_ORM = {
    'connections': {
        'default': settings.db_url,
    },
    'apps': {
        'models': {
            'models': ['app.db.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'use_tz': True
}
