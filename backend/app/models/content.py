from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(100), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # ELIMINAR TODAS LAS RELACIONES POR AHORA
    # subject = relationship("Subject", back_populates="contents")
    # files = relationship("ContentFile", back_populates="content")