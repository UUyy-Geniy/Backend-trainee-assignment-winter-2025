from pydantic import BaseModel
from .inventory import InventoryResponse
from .transaction import CoinHistoryResponse

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int

class SendCoinResponse(BaseModel):
    message: str
    remaining_coins: int

class BuyItemResponse(BaseModel):
    item: str
    remaining_coins: int

class UserInfoResponse(BaseModel):
    coins: int
    inventory: InventoryResponse
    coin_history: CoinHistoryResponse