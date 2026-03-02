from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String, nullable=False)  # ← Asegúrate que sea content_type
    content_url = Column(String)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    order_index = Column(Integer, default=1)
    duration = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="contents")