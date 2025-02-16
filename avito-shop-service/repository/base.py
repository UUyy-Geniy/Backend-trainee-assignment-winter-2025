from typing import Type, TypeVar, Generic, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import Load

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def _before_creation(self, **kwargs) -> dict:
        return kwargs

    async def get(
        self, 
        *filters,
        options: list[Load] | None = None,
        **filter_by
    ) -> Optional[ModelType]:
        stmt = select(self.model)
        
        if filters:
            stmt = stmt.filter(*filters)
        if filter_by:
            stmt = stmt.filter_by(**filter_by)
        if options:
            for option in options:
                stmt = stmt.options(option)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(
        self, 
        _id: int, 
        options: list[Load] | None = None
    ) -> Optional[ModelType]:
        return await self.get(self.model.id == _id, options=options)

    async def create(self, **kwargs) -> ModelType:
        processed_kwargs = await self._before_creation(**kwargs)
        instance = self.model(**processed_kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, _id: int) -> bool:
        query = delete(self.model).where(self.model.id == _id)
        result = await self.session.execute(query)
        return result.rowcount > 0
