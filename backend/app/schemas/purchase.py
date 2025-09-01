from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class PurchaseBase(BaseModel):
    subject_id: int
    amount: float
    payment_method: str

class PurchaseCreate(PurchaseBase):
    user_id: int

class PurchaseUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    payment_id: Optional[str] = None

class Purchase(PurchaseBase):
    id: int
    user_id: int
    status: PaymentStatus
    payment_id: Optional[str] = None
    purchased_at: datetime

    class Config:
        from_attributes = True

# Basic info only
class PurchaseInfo(BaseModel):
    id: int
    status: PaymentStatus
    purchased_at: datetime

    class Config:
        from_attributes = True

class PurchaseWithDetails(Purchase):
    # Use string forward references to avoid circular imports
    user: "User"
    subject: "Subject"

    class Config:
        from_attributes = True