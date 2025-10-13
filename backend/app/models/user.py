from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..database import Base

class UserRole(PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String(50), default="student", nullable=False)  # ← Cambiar a String
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    @property
    def role_enum(self):
        """Convertir string a enum para uso en código"""
        return UserRole(self.role)