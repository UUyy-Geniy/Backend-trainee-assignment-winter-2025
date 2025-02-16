from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_async_engine(
    DATABASE_URI,
    pool_size=100,
    max_overflow=10,
    pool_pre_ping=True
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
