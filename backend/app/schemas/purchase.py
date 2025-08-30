from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.purchase import PaymentStatus

class PurchaseBase(BaseModel):
    subject_id: int

class PurchaseCreate(PurchaseBase):
    user_id: int
    amount: float
    payment_method: str

class PurchaseUpdate(BaseModel):
    payment_id: Optional[str] = None
    status: Optional[PaymentStatus] = None

class Purchase(PurchaseBase):
    id: int
    user_id: int
    amount: float
    payment_id: Optional[str] = None
    payment_method: str
    status: PaymentStatus
    purchased_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseWithDetails(Purchase):
    user: 'User'
    subject: 'Subject'