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