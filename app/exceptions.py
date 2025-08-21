class NotFoundRecordError(Exception):
    pass


class AlreadyExistError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class AlreadyAuthenticatedError(Exception):
    pass

class NotAuthenticatedError(Exception):
    pass

class GetClientError(Exception):
    pass


class UpdateRecordError(Exception):
    pass


class MuchTooManyChannelsError(Exception):
    pass


class UnsupportedTaskTypeError(Exception):
    pass

class DeleteRunningTaskError(Exception):
    pass


class DuplicateRunningTaskError(Exception):
    pass