import pytest
from httpx import AsyncClient
from exceptions.app_exception import InvalidCredentialsError


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    with pytest.raises(InvalidCredentialsError) as exc_info:
        await client.get(
            "/info",
            headers={"Authorization": "Bearer invalid_token"}
        )

    exception = exc_info.value
    assert exception.status_code == 401
    assert exception.message == "Invalid credentials"
    assert exception.details == (
        {"detail": "Could not validate credentials"},
    )
