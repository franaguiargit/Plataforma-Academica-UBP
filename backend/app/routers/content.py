from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.content import Content
from ..models.subject import Subject
from ..models.user import User
from ..schemas.content import ContentCreate, ContentRead, ContentUpdate
from ..utils.security import require_teacher_or_admin, require_student_or_above

router = APIRouter(prefix="/content", tags=["content"])

@router.post("/", response_model=ContentRead)
def create_content(
    content: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    # Verificar que la materia existe
    subject = db.query(Subject).filter(Subject.id == content.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db_content = Content(**content.dict())
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@router.get("/subject/{subject_id}", response_model=List[ContentRead])
def get_content_by_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student_or_above)
):
    content = db.query(Content).filter(Content.subject_id == subject_id).all()
    return content

@router.get("/{content_id}", response_model=ContentRead)
def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_student_or_above)
):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content