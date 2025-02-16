from typing import Optional

from models import User
from repository.base import BaseRepository
from security import get_password_hash

class UserRepository(BaseRepository[User]):

    async def _before_creation(self, **kwargs) -> dict:
        raw_password = kwargs.pop("password")
        kwargs["password_hash"] = get_password_hash(raw_password)
        return kwargs
    
    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.get(username=username)

    async def update_coins(self, user_id: int, delta: int) -> User:
        user = await self.get(user_id)
        user.coins += delta
        
        if user.coins < 0:
            raise ValueError("Negative balance not allowed")
            
        await self.session.flush()
        return user