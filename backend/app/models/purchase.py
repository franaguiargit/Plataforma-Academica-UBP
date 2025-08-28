from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_id = Column(String)  # ID de MercadoPago
    payment_method = Column(String)  # 'mercadopago', 'transfer', etc.
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="purchases")
    subject = relationship("Subject", back_populates="purchases")