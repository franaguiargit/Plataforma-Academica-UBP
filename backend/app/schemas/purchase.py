from __future__ import annotations
from enum import Enum
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

if TYPE_CHECKING:
    from .user import UserRead
    from .subject import SubjectRead

class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class PurchaseBase(BaseModel):
    user_id: int
    subject_id: int
    amount: float

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseRead(PurchaseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[Decimal] = None

# Schemas con detalles (usando forward refs)
class PurchaseWithUserRead(PurchaseRead):
    user: Optional["UserRead"] = None

class PurchaseWithSubjectRead(PurchaseRead):
    subject: Optional["SubjectRead"] = None

class PurchaseWithDetailsRead(PurchaseRead):
    user: Optional["UserRead"] = None
    subject: Optional["SubjectRead"] = None

# Para compatibilidad con código existente
Purchase = PurchaseRead