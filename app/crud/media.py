from .base import BaseCRUD
from app.db.models.media import MediaModel


class MediaCRUD(BaseCRUD[MediaModel]):
    def __init__(self):
        super().__init__(MediaModel)