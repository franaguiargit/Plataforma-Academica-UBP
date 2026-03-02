from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.subject import Subject
from app.models.content import Content
from app.models.purchase import Purchase
from app.models.user import User
from app.routers.auth import get_current_admin_or_teacher  # ✅ Solo importar esta

router = APIRouter(prefix="/subjects", tags=["subjects"])

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

class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=SubjectResponse)
def create_subject(
    subject: SubjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_teacher)
):
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.get("/", response_model=List[SubjectResponse])
def read_subjects(
    skip: Optional[int] = 0, 
    limit: Optional[int] = 100, 
    db: Session = Depends(get_db)
):
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectResponse)
def read_subject(
    subject_id: int,
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_teacher)
):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, value in subject.dict(exclude_unset=True).items():
        setattr(db_subject, key, value)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_teacher)
):
    """
    Eliminar una materia y todo su contenido asociado
    """
    print(f"🗑️ Eliminando materia ID: {subject_id}")
    
    # Buscar la materia
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    try:
        # PRIMERO: Eliminar todo el contenido asociado
        contents = db.query(Content).filter(Content.subject_id == subject_id).all()
        for content in contents:
            print(f"  🗑️ Eliminando contenido: {content.title}")
            db.delete(content)
        
        # SEGUNDO: Eliminar las compras asociadas
        purchases = db.query(Purchase).filter(Purchase.subject_id == subject_id).all()
        for purchase in purchases:
            print(f"  🗑️ Eliminando compra ID: {purchase.id}")
            db.delete(purchase)
        
        # TERCERO: Eliminar la materia
        print(f"  🗑️ Eliminando materia: {subject.title}")
        db.delete(subject)
        
        # COMMIT de todo junto
        db.commit()
        
        print(f"✅ Materia {subject_id} eliminada exitosamente")
        return {"message": "Materia eliminada exitosamente"}
        
    except Exception as e:
        print(f"❌ Error eliminando materia: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminando materia: {str(e)}")