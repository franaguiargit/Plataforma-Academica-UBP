from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    year: int
    semester: int
    price: float

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class Subject(SubjectBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema con contenidos incluidos
class SubjectWithContents(Subject):
    contents: List['Content'] = []