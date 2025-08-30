from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema compartido
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

# Schema para crear usuario
class UserCreate(UserBase):
    password: str

# Schema para actualizar usuario
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Schema para respuestas (sin contraseña)
class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema para login
class UserLogin(BaseModel):
    username: str
    password: str

# Schema para token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None