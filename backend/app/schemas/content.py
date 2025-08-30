from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    order: int = 0
    is_free: bool = False

class ContentCreate(ContentBase):
    subject_id: int

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_free: Optional[bool] = None
    is_active: Optional[bool] = None

class Content(ContentBase):
    id: int
    subject_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContentWithFiles(Content):
    files: List['ContentFile'] = []

# Archivo de contenido
class ContentFileBase(BaseModel):
    filename: str
    file_type: str

class ContentFileCreate(ContentFileBase):
    content_id: int
    file_url: str
    file_size: Optional[int] = None

class ContentFile(ContentFileBase):
    id: int
    file_url: str
    file_size: Optional[int] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True