import sys
import os
# Añadir el directorio backend al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import get_password_hash

def create_test_users():
    db = SessionLocal()
    try:
        # Usuario student (el original fran)
        student_user = User(
            username="fran",
            email="fran@example.com",
            full_name="Fran Test",
            hashed_password=get_password_hash("secret"),
            role=UserRole.STUDENT,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Usuario admin
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add_all([student_user, admin_user])
        db.commit()
        print("Test users created successfully!")
        print("Student: fran/secret")
        print("Admin: admin/admin123")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()