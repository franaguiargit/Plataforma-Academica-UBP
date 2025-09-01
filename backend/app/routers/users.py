from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from ..database import get_db
from ..models import User
from ..schemas import User as UserSchema, UserUpdate
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Obtener mi perfil"""
    return current_user

@router.put("/me", response_model=UserSchema)
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

@router.get("/me/purchases", response_model=list[UserSchema])
def read_user_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Obtener mis materias compradas"""
    # Aquí retornaremos las compras del usuario
    # Por ahora retornamos lista vacía
    return []