from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class SubjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal

class SubjectCreate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None

# Para compatibilidad con código existente
Subject = SubjectRead

# DTO con contenidos - definir después para evitar problemas circulares
class SubjectWithContents(SubjectRead):
    contents: List["ContentRead"] = []

# Resolver forward references después de definir todos los schemas
def resolve_forward_refs():
    from .content import ContentRead
    SubjectWithContents.model_rebuild()