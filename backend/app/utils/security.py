from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..database import get_db
from ..models.user import User, UserRole
from .jwt import decode_token, SECRET_KEY, ALGORITHM

# Configuración
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Configuración de seguridad
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones de contraseña
def verify_password(plain_password, hashed_password):
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

# Funciones de JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Funciones de autenticación
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # ← debe coincidir con lo que ponemos en el token
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()  # ← buscar por username
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario esté activo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Funciones de autorización por roles
def require_role(required_role: UserRole):
    """Factory para crear depends que requieren un rol específico"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_active_user)):
    """Requiere rol admin"""
    if current_user.role != "admin":  # ← Comparar con string
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin required"
        )
    return current_user

def require_teacher_or_admin(current_user: User = Depends(get_current_active_user)):
    """Requiere rol teacher o admin"""
    if current_user.role not in ["teacher", "admin"]:  # ← Comparar con strings
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Teacher or admin required"
        )
    return current_user

def require_student_or_above(current_user: User = Depends(get_current_active_user)):
    """Cualquier usuario autenticado (student, teacher, admin)"""
    return current_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user