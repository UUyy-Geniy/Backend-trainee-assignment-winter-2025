import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_successful_coin_transfer(client: AsyncClient, test_user: dict):
    await client.post("/auth", json={
        "username": "receiver_user",
        "password": "receiver_pass"
    })
    
    response = await client.post(
        "/sendCoin",
        json={"toUser": "receiver_user", "amount": 300},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    
    assert response.status_code == 200
    assert response.json()["remaining_coins"] == 700
    
    sender_info = await client.get(
        "/info",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert sender_info.json()["coins"] == 700
    
    assert len(sender_info.json()["coin_history"]["sent"]) == 1
    assert sender_info.json()["coin_history"]["sent"][0]["amount"] == 300

@pytest.mark.parametrize("invalid_transfer", [
    {"toUser": "non_existent_user", "amount": 100},  # invalid user
    {"toUser": "test_user", "amount": 100},          # self-transfer
    {"toUser": "receiver", "amount": -100},          # negative amount
    {"toUser": "receiver", "amount": 2000},          # insufficient funds
    {"toUser": "receiver", "amount": 0},             # zero amount
])
@pytest.mark.asyncio
async def test_invalid_transfers(client: AsyncClient, test_user: dict, invalid_transfer: dict):
    with pytest.raises(ValueError) as exc_info:
        await client.post(
            "/sendCoin",
            json=invalid_transfer,
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
    
    exception = exc_info.value
    assert exception.status_code >= 400