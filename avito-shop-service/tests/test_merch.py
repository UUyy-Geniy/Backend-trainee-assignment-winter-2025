import pytest
from httpx import AsyncClient
from exceptions.app_exception import ItemNotFoundError

@pytest.mark.asyncio
async def test_successful_item_purchase(client: AsyncClient, test_user: dict):
    response = await client.get(
        f"/buy/book",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    
    assert response.status_code == 200
    assert response.json()["remaining_coins"] == 950
    assert response.json()["item"] == 'book'
    
    info_response = await client.get(
        "/info",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    inventory = info_response.json()["inventory"]["inventory"]
    assert any(item["type"] == 'book' for item in inventory)

@pytest.mark.asyncio
async def test_purchase_nonexistent_item(client: AsyncClient, test_user: dict):
    with pytest.raises(ItemNotFoundError) as exc_info:
        await client.get(
            "/buy/non_existent_item",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
    
    exception = exc_info.value
    assert exception.status_code == 404
    assert exception.message == "Item not found"
    assert exception.details == {"item_name": "non_existent_item"}