from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserRead
from ..schemas.auth import Token  # Corregir import
from ..utils.security import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"sub": user.username, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return current_user