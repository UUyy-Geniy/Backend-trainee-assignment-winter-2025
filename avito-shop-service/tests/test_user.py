import pytest
from httpx import AsyncClient
from exceptions.app_exception import InvalidCredentialsError

@pytest.mark.asyncio
async def test_get_user_info(client: AsyncClient, test_user: dict):
    response = await client.get(
        "/info",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["coins"] == 1000
    assert isinstance(data["inventory"]["inventory"], list)

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await client.get("/info")
    
    exception = exc_info.value
    assert exception.status_code == 401