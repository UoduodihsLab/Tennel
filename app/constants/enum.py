from enum import IntEnum

class UserRoleEnum(IntEnum):
    ADMIN = 1
    USER = 2


class ChannelStatus(IntEnum):
    UNSYNCED = 1
    SYNCED = 2


class AccountRole(IntEnum):
    OWNER = 1
    ADMIN = 2
    MEMBER = 3


class TaskType(IntEnum):
    CREATE_CHANNEL = 1
    SET_USERNAME = 2
    SET_PHOTO = 3
    SET_ACCOUNT = 4
    SET_TITLE = 5


class TaskStatus(IntEnum):
    PENDING = 1
    RUNNING = 2
    COMPLETED = 3
