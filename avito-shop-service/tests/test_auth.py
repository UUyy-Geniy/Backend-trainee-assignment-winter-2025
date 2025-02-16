import pytest
from httpx import AsyncClient

@pytest.mark.parametrize("user_data", [
    {"username": "user1", "password": "pass1"},
])
@pytest.mark.asyncio
async def test_successful_registration(client: AsyncClient, user_data: dict):
    response = await client.post("/auth", json=user_data)
    assert response.status_code == 200
    assert "token" in response.json()
