from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from ..database import get_db
from ..models import Subject, Purchase
from ..schemas.subject import (
    Subject as SubjectSchema,
    SubjectCreate,
    SubjectUpdate,
    SubjectWithContents
)
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("/", response_model=List[SubjectSchema])
def read_subjects(
    skip: int = 0,
    limit: int = 100,
    year: Optional[int] = None,
    semester: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Any:
    """Obtener lista de materias con filtros opcionales"""
    query = db.query(Subject).filter(Subject.is_active == True)
    
    if year:
        query = query.filter(Subject.year == year)
    if semester:
        query = query.filter(Subject.semester == semester)
    if search:
        query = query.filter(Subject.name.ilike(f"%{search}%"))
    
    subjects = query.offset(skip).limit(limit).all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectWithContents)
def read_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """Obtener detalle de una materia"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.is_active == True
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    return subject