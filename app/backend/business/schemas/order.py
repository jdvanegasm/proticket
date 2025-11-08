from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class OrderBase(BaseModel):
    event_id: int
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: str

class OrderOut(BaseModel):
    id_order: int
    buyer_id: UUID
    event_id: int
    quantity: int
    total_price: Decimal
    status: str
    created_at: datetime

    class Config:        
        from_attributes = True