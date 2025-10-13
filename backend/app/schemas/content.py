from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str  # 'video', 'document', 'quiz', etc.
    subject_id: int

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None

class ContentRead(ContentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True