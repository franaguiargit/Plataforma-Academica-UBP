from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relaciones - definir solo si necesitamos
    # contents = relationship("Content", back_populates="subject")
    # purchases = relationship("Purchase", back_populates="subject")