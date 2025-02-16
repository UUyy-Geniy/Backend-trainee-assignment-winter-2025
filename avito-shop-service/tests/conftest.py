import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from app.app import app
from models import Base
from core.config import settings
import pytest_asyncio
import logging

@pytest_asyncio.fixture(scope="session")
async def test_db():
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def client(test_db):
    async with AsyncClient(app=app, base_url="http://localhost/api/v1") as client:
        yield client

@pytest_asyncio.fixture
async def test_user(client: AsyncClient):
    user_data = {"username": "test_user", "password": "test_pass"}
    response = await client.post("/auth", json=user_data)
    return {
        "data": user_data,
        "token": response.json()["token"],
        "id": response.json().get("user_id")
    }