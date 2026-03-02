from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # ✅ AGREGAR ESTA LÍNEA
from sqlalchemy.orm import Session
import os  # ✅ AGREGAR
from pathlib import Path  # ✅ AGREGAR

from app.routers import auth, users, subjects, content, purchases
from app.database import get_db
from app.utils.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.purchase import Purchase

# Crear la aplicación
app = FastAPI(
    title="Plataforma Académica UBP",
    description="API para plataforma educativa",
    version="1.0.0"
)

# ✅ AGREGAR ESTAS LÍNEAS DESPUÉS DE crear app:
# Crear directorio uploads si no existe
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

# Servir archivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS CRÍTICO para conectar frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Incluir routers CON prefixes
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(subjects.router, tags=["subjects"])
app.include_router(content.router, tags=["content"])
app.include_router(purchases.router, tags=["purchases"])

@app.get("/")
def read_root():
    return {"message": "Plataforma Académica UBP API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/stats")
def get_platform_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estadísticas globales de la plataforma (admin) o personales (student)"""
    from sqlalchemy import func as sqlfunc

    total_subjects = db.query(Subject).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_purchases = db.query(Purchase).count()
    total_revenue = db.scalar(sqlfunc.coalesce(sqlfunc.sum(Purchase.amount), 0))

    # Compras por materia
    subject_stats = (
        db.query(
            Purchase.subject_id,
            sqlfunc.count(Purchase.id).label("purchase_count"),
            sqlfunc.sum(Purchase.amount).label("revenue"),
        )
        .group_by(Purchase.subject_id)
        .all()
    )
    per_subject = {
        row.subject_id: {"purchases": row.purchase_count, "revenue": float(row.revenue or 0)}
        for row in subject_stats
    }

    return {
        "total_subjects": total_subjects,
        "total_students": total_students,
        "total_purchases": total_purchases,
        "total_revenue": float(total_revenue),
        "per_subject": per_subject,
    }