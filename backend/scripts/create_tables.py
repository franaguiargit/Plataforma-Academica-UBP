import sys
import os
# Añadir el directorio backend al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
# Importar todos los modelos para que se registren con Base
from app.models import User, Subject, Content, ContentFile, Purchase, RefreshToken

def create_tables():
    """Crear todas las tablas definidas en los modelos"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        
        # Mostrar qué tablas se crearon
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {tables}")
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()