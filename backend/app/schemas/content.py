from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str  # 'video', 'document', 'quiz', etc.
    subject_id: int

class ContentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    content_url: str
    subject_id: int
    order_index: Optional[int] = 1
    duration: Optional[int] = None  # ✅ Cambiar a Optional

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    subject_id: Optional[int] = None
    order_index: Optional[int] = None
    duration: Optional[int] = None  # ✅ Cambiar a Optional

class ContentRead(ContentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContentOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    content_url: str
    subject_id: int
    order_index: int
    duration: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True