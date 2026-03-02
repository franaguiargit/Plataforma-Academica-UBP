from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SubjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class SubjectRead(SubjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubjectOut(SubjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Para compatibilidad con código existente
Subject = SubjectRead

# DTO con contenidos - definir después para evitar problemas circulares
class SubjectWithContents(SubjectRead):
    contents: List["ContentRead"] = []

# Resolver forward references después de definir todos los schemas
def resolve_forward_refs():
    from .content import ContentRead
    SubjectWithContents.model_rebuild()