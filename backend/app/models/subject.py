from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    year = Column(Integer, nullable=False)  # Año de la carrera (1-5)
    semester = Column(Integer, nullable=False)  # Semestre (1 o 2)
    price = Column(Float, nullable=False)  # Precio en pesos argentinos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    contents = relationship("Content", back_populates="subject", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="subject")