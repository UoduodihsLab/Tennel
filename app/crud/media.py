from .base import BaseCRUD
from app.db.models.media import MediaModel
from ..constants.enum import MediaType
from typing import List


class MediaCRUD(BaseCRUD[MediaModel]):
    def __init__(self):
        super().__init__(MediaModel)

    async def get_medias_by_m_type(self, m_type: MediaType) -> List[str]:
        return await self.model.filter(m_type=m_type).values_list('filename', flat=True)

    async def get_medias_by_user_id_and_m_type(self, user_id: int, m_type: MediaType) -> List[str]:
        return await self.model.filter(m_type=m_type, user_id=user_id).values_list('filename', flat=True)