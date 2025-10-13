from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database import Base

class ContentFile(Base):
    __tablename__ = "content_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # ELIMINAR RELACIONES
    # content = relationship("Content", back_populates="files")

