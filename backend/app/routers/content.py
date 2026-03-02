from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.content import Content
from app.models.user import User
from app.schemas.content import ContentCreate, ContentUpdate
from app.utils.security import get_current_active_user
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/content")

@router.post("/upload", response_model=None)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Subir archivo de contenido"""
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    # Validar tipo de archivo
    allowed_extensions = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.mp4', '.avi', '.mov'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_extensions)}"
        )
    
    # Crear directorio uploads si no existe
    upload_dir = Path("uploads/content")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre único
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename
    
    # Guardar archivo
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Retornar URL relativa
        file_url = f"/uploads/content/{unique_filename}"
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "url": file_url,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando archivo: {str(e)}")

@router.get("/", response_model=None)
async def get_all_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    content = db.query(Content).all()
    result = []
    for item in content:
        result.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "type": item.content_type,
            "content_type": item.content_type,
            "content_url": item.content_url,
            "subject_id": item.subject_id,
            "order_index": item.order_index,
            "duration": item.duration,
            "created_at": item.created_at.isoformat() if item.created_at else None
        })
    return result

@router.get("/{content_id}", response_model=None)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    return {
        "id": content.id,
        "title": content.title,
        "description": content.description,
        "type": content.content_type,
        "content_type": content.content_type,
        "content_url": content.content_url,
        "subject_id": content.subject_id,
        "order_index": content.order_index,
        "duration": content.duration,
        "created_at": content.created_at.isoformat() if content.created_at else None
    }

@router.get("/subjects/{subject_id}/content", response_model=None)
async def get_subject_content(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    content = db.query(Content).filter(Content.subject_id == subject_id).all()
    result = []
    for item in content:
        result.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "type": item.content_type,
            "content_type": item.content_type,
            "content_url": item.content_url,
            "subject_id": item.subject_id,
            "order_index": item.order_index,
            "duration": item.duration,
            "created_at": item.created_at.isoformat() if item.created_at else None
        })
    return result

@router.post("/", response_model=None)
async def create_content(
    content: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    db_content = Content(
        title=content.title,
        description=content.description,
        content_type=content.content_type,
        content_url=content.content_url,
        subject_id=content.subject_id,
        order_index=getattr(content, 'order_index', 1),
        duration=getattr(content, 'duration', None)
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    return {
        "id": db_content.id,
        "title": db_content.title,
        "description": db_content.description,
        "type": db_content.content_type,
        "content_type": db_content.content_type,
        "content_url": db_content.content_url,
        "subject_id": db_content.subject_id,
        "order_index": db_content.order_index,
        "duration": db_content.duration,
        "created_at": db_content.created_at.isoformat() if db_content.created_at else None
    }

@router.put("/{content_id}", response_model=None)
async def update_content(
    content_id: int,
    content: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    for field, value in content.dict(exclude_unset=True).items():
        setattr(db_content, field, value)
    
    db.commit()
    db.refresh(db_content)
    
    return {
        "id": db_content.id,
        "title": db_content.title,
        "description": db_content.description,
        "type": db_content.content_type,
        "content_type": db_content.content_type,
        "content_url": db_content.content_url,
        "subject_id": db_content.subject_id,
        "order_index": db_content.order_index,
        "duration": db_content.duration,
        "created_at": db_content.created_at.isoformat() if db_content.created_at else None
    }

@router.delete("/{content_id}", response_model=None)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    db.delete(db_content)
    db.commit()
    return {"message": "Contenido eliminado exitosamente"}