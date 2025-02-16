import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_user_workflow(client: AsyncClient):
    """Полный цикл работы пользователя: регистрация -> покупка -> перевод"""
    register_response = await client.post("/auth", json={
        "username": "new_user",
        "password": "secure_pass123"
    })
    assert register_response.status_code == 200
    token = register_response.json()["token"]

    info_response = await client.get(
        "/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert info_response.json()["coins"] == 1000

    # Покупка товара
    buy_response = await client.get(
        "/buy/book",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert buy_response.status_code == 200
    assert buy_response.json() == {
        "item": "book",
        "remaining_coins": 950,
    }

    await client.post("/auth", json={
        "username": "receiver_user",
        "password": "receiver_pass123"
    })

    transfer_response = await client.post(
        "/sendCoin",
        json={"toUser": "receiver_user", "amount": 200},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert transfer_response.status_code == 200
    assert transfer_response.json() == {
        "message": "Coins sent successfully",
        "remaining_coins": 500
    }

    final_info = await client.get(
        "/info",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert final_info.json()["coins"] == 500
    assert len(final_info.json()["coin_history"]["sent"]) == 1
    assert any(item["type"] == "book" 
              for item in final_info.json()["inventory"]["inventory"])

@pytest.mark.parametrize("invalid_data, expected_status", [
    ({"username": "short", "password": "pass"}, 400),  # Недостаточная длина пароля
    ({"username": "invalid@user", "password": "good_pass"}, 400),  # Недопустимые символы
    ({"username": "existing_user", "password": ""}, 400),  # Пустой пароль
])
@pytest.mark.asyncio
async def test_invalid_registration(client: AsyncClient, invalid_data, expected_status):
    response = await client.post("/auth", json=invalid_data)
    assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_insufficient_funds(client: AsyncClient):
    auth_response = await client.post("/auth", json={
        "username": "poor_user",
        "password": "poor_pass"
    })
    token = auth_response.json()["token"]

    response = await client.post(
        "/sendCoin",
        json={"toUser": "non_existent", "amount": 5000},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "Insufficient coins" in response.json()["detail"]