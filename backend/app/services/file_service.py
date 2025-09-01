import os
from fastapi import UploadFile, HTTPException
from typing import Optional
import shutil
from datetime import datetime

# Por ahora usaremos almacenamiento local
# Después migraremos a Cloudinary o S3
UPLOAD_DIR = "uploads"

# Crear directorio si no existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload_file(
    file: UploadFile,
    folder: str = "general"
) -> dict:
    """Subir un archivo y retornar su información"""
    # Validar tipo de archivo
    allowed_types = ["application/pdf", "video/mp4", "video/mpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Solo PDF y videos."
        )
    
    # Crear subdirectorio
    subfolder = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(subfolder, exist_ok=True)
    
    # Generar nombre único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(subfolder, filename)
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Retornar información
    return {
        "filename": filename,
        "file_url": f"/{file_path}",  # En producción será URL de Cloudinary
        "file_type": file.content_type,
        "file_size": os.path.getsize(file_path)
    }

def delete_file(file_path: str) -> bool:
    """Eliminar un archivo"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False