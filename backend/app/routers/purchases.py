from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from ..database import get_db
from ..models.purchase import Purchase
from ..models.subject import Subject
from ..models.user import User
from ..schemas.purchase import PurchaseCreate, PurchaseRead
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/purchases", tags=["purchases"])

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