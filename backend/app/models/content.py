from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String, nullable=False)  # 'pdf', 'video', 'link', etc.
    order = Column(Integer, default=0)  # Para ordenar el contenido
    is_free = Column(Boolean, default=False)  # Contenido de muestra gratuito
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    subject = relationship("Subject", back_populates="contents")
    files = relationship("ContentFile", back_populates="content", cascade="all, delete-orphan")