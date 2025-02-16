from pydantic import BaseModel
from typing import List

class InventoryItem(BaseModel):
    type: str
    quantity: int

class InventoryResponse(BaseModel):
    inventory: List[InventoryItem]