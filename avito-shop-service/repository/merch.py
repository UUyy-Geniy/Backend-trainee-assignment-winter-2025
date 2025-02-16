from typing import Optional

from models import MerchItem
from repository.base import BaseRepository


class MerchRepository(BaseRepository[MerchItem]):
    async def get_by_name(self, name: str) -> Optional[MerchItem]:
        return await self.get(name=name)