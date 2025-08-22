from enum import IntEnum


class UserRole(IntEnum):
    ADMIN = 1
    USER = 2


class AccountRole(IntEnum):
    OWNER = 1
    ADMIN = 2
    MEMBER = 3


class TaskType(IntEnum):
    CREATE_CHANNEL = 1
    SET_USERNAME = 2
    SET_PHOTO = 3
    SET_DESCRIPTION = 4
    SET_ACCOUNT = 5
    SET_TITLE = 6


class TaskStatus(IntEnum):
    PENDING = 1
    RUNNING = 2
    COMPLETED = 3


class MediaType(IntEnum):
    AVATAR = 1
    IMAGE = 2
    VIDEO = 3


class ScheduleType(IntEnum):
    PUBLISH_MESSAGE = 1
    SYNC_CHANNELS = 2

class ScheduleStatus(IntEnum):
    PENDING = 1
    RUNNING = 2
