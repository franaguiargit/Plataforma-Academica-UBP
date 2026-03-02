import sys
import os

# Ajustar path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Verificar si existe
    result = db.execute(text("PRAGMA table_info(content)")).fetchall()
    columns = [row[1] for row in result]
    
    if 'order_index' not in columns:
        db.execute(text("ALTER TABLE content ADD COLUMN order_index INTEGER DEFAULT 1"))
        db.commit()
        print("✅ Columna order_index agregada")
    else:
        print("⚠️ Columna order_index ya existe")
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()