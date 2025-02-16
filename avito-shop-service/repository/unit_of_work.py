from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from models import MerchItem, Transaction, User, Purchase
from repository.merch import MerchRepository
from repository.transaction import TransactionRepository
from repository.user import UserRepository
from repository.purchase import PurchaseRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(User, session)
        self.merch = MerchRepository(MerchItem, session)
        self.transactions = TransactionRepository(Transaction, session)
        self.purchases = PurchaseRepository(Purchase, session)
    
    async def __aenter__(self):
        return self

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def __aexit__(self, *args):
        await self.rollback()

    @asynccontextmanager
    async def atomic(self):
        try:
            yield
            await self.commit()
        except Exception:
            await self.rollback()
            raise


