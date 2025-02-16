from pydantic import BaseModel
from typing import List

class TransactionInfo(BaseModel):
    fromUser: str
    toUser: str
    amount: int
    timestamp: str

class CoinHistoryResponse(BaseModel):
    received: List[TransactionInfo]
    sent: List[TransactionInfo]