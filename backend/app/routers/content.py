from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import Any, List

from ..database import get_db
from ..models import Content, ContentFile
from ..schemas.content import (
    Content as ContentSchema,
    ContentCreate,
    ContentUpdate,
    ContentWithFiles,
    ContentFileRead,
    ContentFileCreate
)
from ..services.file_service import upload_file
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/content", tags=["content"])

@router.get("/{content_id}", response_model=ContentWithFiles)
def read_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """Obtener detalle de un contenido específico"""
    # Obtener el contenido
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.is_active == True
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    # Verificar acceso
    if not content.is_free:
        has_access = db.query(Purchase).filter(
            Purchase.user_id == current_user.id,
            Purchase.subject_id == content.subject_id,
            Purchase.status == "approved"
        ).first()
        
        if not has_access:
            raise HTTPException(
                status_code=403, 
                detail="No tienes acceso a este contenido. Debes comprar la materia."
            )
    
    return content

@router.get("/subject/{subject_id}", response_model=List[ContentSchema])
def read_contents_by_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """Obtener todos los contenidos de una materia"""
    # Verificar que la materia existe
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.is_active == True
    ).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    # Verificar si tiene acceso
    has_access = db.query(Purchase).filter(
        Purchase.user_id == current_user.id,
        Purchase.subject_id == subject_id,
        Purchase.status == "approved"
    ).first() is not None
    
    # Obtener contenidos
    query = db.query(Content).filter(
        Content.subject_id == subject_id,
        Content.is_active == True
    )
    
    # Si no tiene acceso, solo mostrar contenido gratuito
    if not has_access:
        query = query.filter(Content.is_free == True)
    
    contents = query.order_by(Content.order).all()
    return contents

@router.post("/{content_id}/upload", response_model=ContentFileRead)
async def upload_content_file(
    content_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """Subir un archivo para un contenido"""
    # TODO: Verificar que el usuario es admin o profesor
    
    # Verificar que el contenido existe
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    # Subir archivo
    file_info = await upload_file(file, folder=f"content_{content_id}")
    
    # Guardar en base de datos
    db_file = ContentFile(
        content_id=content_id,
        filename=file_info["filename"],
        file_url=file_info["file_url"],
        file_type=file_info["file_type"],
        file_size=file_info["file_size"]
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file