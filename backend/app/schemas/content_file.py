from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContentFileBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    content_id: int

class ContentFileCreate(ContentFileBase):
    pass

class ContentFileRead(ContentFileBase):
    id: int
    file_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContentFileUpdate(BaseModel):
    filename: Optional[str] = None
    file_type: Optional[str] = None

# Para compatibilidad con código existente
ContentFile = ContentFileRead