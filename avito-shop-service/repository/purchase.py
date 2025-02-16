from typing import Optional

from .base import BaseRepository
from models import Purchase

class PurchaseRepository(BaseRepository[Purchase]):
    async def get_by_user_id_and_item_name(self, user_id: int, item_name: str) -> Optional[Purchase]:
        return await self.get(user_id=user_id, item_name=item_name)