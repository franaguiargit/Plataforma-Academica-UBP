from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ContentFileBase(BaseModel):
    filename: str
    file_url: str
    file_type: str
    file_size: Optional[int] = None

class ContentFileCreate(ContentFileBase):
    content_id: int

class ContentFileRead(ContentFileBase):
    id: int
    content_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

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
    files: List[ContentFileRead] = []

    class Config:
        from_attributes = True