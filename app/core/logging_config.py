# app/core/logging_config.py

import logging.config
from typing import Dict

# 从中央配置导入 settings 实例
from app.core.config import settings

# 日志文件将被创建在项目根目录下的 'logs' 文件夹中
LOG_DIR = settings.BASE_DIR / "logs"

LOGGING_CONFIG: Dict[str, any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_formatter": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s [%(name)s] :: %(message)s",
            "use_colors": True,
        },
        # "json_formatter": {
        #     "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        #     "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        #     "rename_fields": {"levelname": "level", "asctime": "timestamp"},
        # },
        "file_formatter": {
            "class": "logging.Formatter",
            "format": "%(asctime)s | %(levelname)-8s | [%(name)s:%(lineno)d] | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
            "stream": "ext://sys.stdout",
        },
        "app_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file_formatter",
            "filename": LOG_DIR / "tennel.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "access_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file_formatter",
            "filename": LOG_DIR / "tennel-access.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        # 根 logger
        "": {
            "handlers": ["console_handler", "app_file_handler"],
            "level": settings.LOG_LEVEL.upper(),
        },
        "uvicorn.error": {
            "handlers": ["console_handler", "app_file_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console_handler", "access_file_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logging():
    """
    加载并应用日志配置。
    """
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
