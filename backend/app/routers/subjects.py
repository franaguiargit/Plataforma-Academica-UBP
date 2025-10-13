from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.subject import Subject
from ..models.user import User
from ..schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate
from ..utils.security import get_current_active_user, require_teacher_or_admin, require_student_or_above

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.post("/", response_model=SubjectRead)
def create_subject(
    subject: SubjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.get("/", response_model=List[SubjectRead])
def read_subjects(
    skip: Optional[int] = 0, 
    limit: Optional[int] = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student_or_above)
):
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return subjects

@router.get("/{subject_id}", response_model=SubjectRead)
def read_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student_or_above)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/{subject_id}", response_model=SubjectRead)
def update_subject(
    subject_id: int,
    subject: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
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
    current_user: User = Depends(require_teacher_or_admin)
):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if db_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(db_subject)
    db.commit()
    return {"message": "Subject deleted successfully"}