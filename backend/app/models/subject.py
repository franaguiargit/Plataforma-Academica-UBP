from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contents = relationship("Content", back_populates="subject")