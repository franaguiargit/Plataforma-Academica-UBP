import os
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def create_access_token(subject: str | int, extra: Dict[str, Any] | None = None) -> str:
    now = datetime.utcnow()
    data = {"sub": str(subject), "type": "access"}
    if extra:
        data.update(extra)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str | int) -> Tuple[str, str, datetime]:
    now = datetime.utcnow()
    jti = str(uuid.uuid4())
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "jti": jti, "type": "refresh", "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expire

def create_email_token(subject: str | int, expire_minutes: int = 60) -> Tuple[str, datetime]:
    """
    Crear token para verify email. Retorna (token, expires_at).
    """
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    payload = {"sub": str(subject), "type": "verify", "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def create_password_token(subject: str | int, expire_minutes: int = 60) -> Tuple[str, datetime]:
    """
    Crear token para resetear contraseña. Retorna (token, expires_at).
    """
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    payload = {"sub": str(subject), "type": "password_reset", "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise e

def decode_access_token(token: str):
    """
    Decodifica un token JWT y devuelve el payload o None si es inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
) -> User:
    # lógica de verificación de token
    pass