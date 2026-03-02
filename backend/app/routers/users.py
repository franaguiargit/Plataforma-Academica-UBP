from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional  # ← Agregado Optional aquí

from ..database import get_db
from ..models import User  # ← Debería estar ya
from ..schemas import UserCreate, UserRead, UserUpdate
from ..utils.security import get_current_active_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Obtener mi perfil"""
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Actualizar mi perfil"""
    # Actualizar solo los campos proporcionados
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Verificar que el nuevo email no esté en uso
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El email ya está en uso"
            )
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/purchases", response_model=List[UserRead])
def read_user_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Obtener mis materias compradas"""
    # Aquí retornaremos las compras del usuario
    # Por ahora retornamos lista vacía
    return []

@router.get("/", response_model=List[UserRead])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todos los usuarios (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserRead)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo usuario (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    # Verificar si el username ya existe
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Verificar si el email ya existe
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="El email ya está en uso")
    
    # Crear nuevo usuario
    from app.utils.security import get_password_hash
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        role=user.role if isinstance(user.role, str) else user.role.value,  # ✅ Convertir a string
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/purchases/{user_id}", response_model=None)
def get_user_purchases(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener compras de un usuario específico (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    from app.models.purchase import Purchase
    purchases = db.query(Purchase).filter(Purchase.user_id == user_id).all()
    return purchases

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar usuario (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}