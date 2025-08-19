from app.db.models import ChannelModel
from .base import BaseCRUD


class ChannelCRUD(BaseCRUD[ChannelModel]):
    def __init__(self):
        super().__init__(ChannelModel)