from app.db.models.task import TaskModel
from .base import BaseCRUD


class TaskCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(TaskModel)
