from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List
from pydantic import BaseModel

from ..database import get_db
from ..models.purchase import Purchase
from ..models.subject import Subject
from ..models.user import User
from ..schemas.purchase import PurchaseCreate, PurchaseRead
from ..utils.security import get_current_active_user
from ..services.mercadopago_service import (
    create_preference,
    get_mp_config_info,
    get_payment_status_label,
)

router = APIRouter(prefix="/purchases", tags=["purchases"])


# ========== Schemas para MercadoPago ==========

class CreatePreferenceRequest(BaseModel):
    subject_id: int

class ConfirmPaymentRequest(BaseModel):
    subject_id: int
    payment_id: str = "simulation"
    payment_status: str = "approved"


# ========== MercadoPago Endpoints ==========

@router.post("/create-preference")
def create_mp_preference(
    request: CreatePreferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Crea una preferencia de pago en MercadoPago.
    En modo simulación, retorna datos para el checkout modal.
    """
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Verificar si ya compró esta materia
    existing = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == current_user.id,
            Purchase.subject_id == request.subject_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ya compraste esta materia")

    preference = create_preference(
        subject_id=subject.id,
        subject_title=subject.title,
        subject_price=float(subject.price),
        user_id=current_user.id,
        user_email=current_user.email,
    )

    return preference


@router.post("/confirm-payment")
def confirm_payment(
    request: ConfirmPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Confirma el pago y registra la compra.
    Se llama después de que MercadoPago aprueba el pago (o simulación).
    """
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Verificar que no tenga compra duplicada
    existing = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == current_user.id,
            Purchase.subject_id == request.subject_id,
        )
        .first()
    )
    if existing:
        # Ya existe, retornarla (idempotente)
        return {
            "message": "Compra ya registrada",
            "purchase_id": existing.id,
            "status": "approved",
            "already_purchased": True,
        }

    if request.payment_status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"El pago no fue aprobado. Estado: {get_payment_status_label(request.payment_status)}",
        )

    # Registrar la compra
    db_purchase = Purchase(
        user_id=current_user.id,
        subject_id=request.subject_id,
        amount=subject.price,
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)

    return {
        "message": "Compra registrada exitosamente",
        "purchase_id": db_purchase.id,
        "status": "approved",
        "payment_id": request.payment_id,
        "subject_title": subject.title,
        "amount": float(subject.price),
    }


@router.get("/mp-config")
def get_mp_config(current_user: User = Depends(get_current_active_user)):
    """Retorna la configuración de MercadoPago (útil para el frontend)"""
    return get_mp_config_info()


# ========== Endpoints originales ==========

@router.post("/", response_model=PurchaseRead)
def create_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verificar que la materia existe
    subject = db.query(Subject).filter(Subject.id == purchase.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Crear compra
    db_purchase = Purchase(
        user_id=current_user.id,
        subject_id=purchase.subject_id,
        amount=subject.price
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

@router.get("/my-purchases", response_model=List[PurchaseRead])
def get_my_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    purchases = db.query(Purchase).filter(Purchase.user_id == current_user.id).all()
    return purchases


@router.get("/recent")
def get_recent_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 20,
):
    """Últimas compras de la plataforma (solo admin/teacher)"""
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="No autorizado")

    rows = (
        db.query(Purchase, User, Subject)
        .join(User, Purchase.user_id == User.id)
        .outerjoin(Subject, Purchase.subject_id == Subject.id)
        .order_by(Purchase.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "user": u.full_name or u.username,
            "user_email": u.email,
            "subject": s.title if s else f"(Materia #{p.subject_id} eliminada)",
            "amount": float(p.amount),
            "date": p.created_at.isoformat() if p.created_at else None,
        }
        for p, u, s in rows
    ]