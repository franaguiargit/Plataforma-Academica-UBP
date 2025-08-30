from .user import User, UserCreate, UserUpdate, UserLogin, Token, TokenData
from .subject import Subject, SubjectCreate, SubjectUpdate, SubjectWithContents
from .content import Content, ContentCreate, ContentUpdate, ContentWithFiles, ContentFile, ContentFileCreate
from .purchase import Purchase, PurchaseCreate, PurchaseUpdate, PurchaseWithDetails

__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate", "UserLogin", "Token", "TokenData",
    # Subject schemas
    "Subject", "SubjectCreate", "SubjectUpdate", "SubjectWithContents",
    # Content schemas
    "Content", "ContentCreate", "ContentUpdate", "ContentWithFiles", 
    "ContentFile", "ContentFileCreate",
    # Purchase schemas
    "Purchase", "PurchaseCreate", "PurchaseUpdate", "PurchaseWithDetails"
]

sqlalchemy.url = sqlite:///./plataforma_ubp.db

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import Base
from app.models import *  # Importar todos los modelos

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata
