from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List

from ..database import get_db
from ..models import Purchase
from ..schemas import Purchase  # usar schema simple para evitar circularidad
from ..utils.security import get_current_active_user

router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.get("/me", response_model=List[Purchase])
def read_my_purchases(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """Obtener mi historial de compras (uso schema simple)"""
    purchases = db.query(Purchase).filter(
        Purchase.user_id == current_user.id
    ).order_by(Purchase.purchased_at.desc()).all()
    
    return purchases