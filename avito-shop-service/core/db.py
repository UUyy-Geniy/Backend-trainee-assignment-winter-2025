from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .engine import async_session
from models import MerchItem

MERCH_ITEMS = [
    {"name": "t-shirt", "price": 80},
    {"name": "cup", "price": 20},
    {"name": "book", "price": 50},
    {"name": "pen", "price": 10},
    {"name": "powerbank", "price": 200},
    {"name": "hoody", "price": 300},
    {"name": "umbrella", "price": 200},
    {"name": "socks", "price": 10},
    {"name": "wallet", "price": 50},
    {"name": "pink-hoody", "price": 500},
]

async def seed_merch_items(session: AsyncSession):
    for item in MERCH_ITEMS:
        result = await session.execute(select(MerchItem).where(MerchItem.name == item["name"]))
        existing_item = result.scalar_one_or_none()

        if not existing_item:
            session.add(MerchItem(**item))

    await session.commit()

async def init_db():
    async with async_session() as session:
        await seed_merch_items(session)