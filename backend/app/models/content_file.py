from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class ContentFile(Base):
    __tablename__ = "content_files"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=False)  # URL de Cloudinary o S3
    file_type = Column(String)  # 'pdf', 'mp4', etc.
    file_size = Column(Integer)  # Tamaño en bytes
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    content = relationship("Content", back_populates="files")