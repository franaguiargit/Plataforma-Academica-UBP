"""
Servicio de MercadoPago - Modo Sandbox/Simulación
Integra con la API real de MercadoPago en modo TEST.
Si no hay credenciales configuradas, funciona en modo simulación.
"""
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")

# Determinar si estamos en modo simulación o real
SIMULATION_MODE = not MP_ACCESS_TOKEN or MP_ACCESS_TOKEN.startswith("TEST-placeholder")


def get_mp_sdk():
    """Obtener instancia del SDK de MercadoPago"""
    if SIMULATION_MODE:
        return None
    try:
        import mercadopago
        return mercadopago.SDK(MP_ACCESS_TOKEN)
    except Exception as e:
        print(f"⚠️ Error inicializando MercadoPago SDK: {e}")
        return None


def create_preference(
    subject_id: int,
    subject_title: str,
    subject_price: float,
    user_id: int,
    user_email: str = "test@test.com"
) -> Dict[str, Any]:
    """
    Crea una preferencia de pago en MercadoPago.
    En modo simulación, retorna datos simulados.
    """
    external_reference = f"purchase_{user_id}_{subject_id}_{uuid.uuid4().hex[:8]}"
    
    if SIMULATION_MODE:
        # Modo simulación - retornar datos que imitan la respuesta de MP
        return {
            "id": f"sim_{uuid.uuid4().hex[:12]}",
            "init_point": None,  # No hay URL real, el frontend usa el modal
            "sandbox_init_point": None,
            "external_reference": external_reference,
            "simulation": True,
            "preference_data": {
                "title": subject_title,
                "price": subject_price,
                "currency": "ARS",
                "subject_id": subject_id,
                "user_id": user_id,
            }
        }
    
    # Modo real con SDK de MercadoPago
    sdk = get_mp_sdk()
    if not sdk:
        raise Exception("No se pudo inicializar MercadoPago SDK")
    
    preference_data = {
        "items": [
            {
                "id": str(subject_id),
                "title": f"Materia: {subject_title}",
                "description": f"Acceso a la materia {subject_title} - Plataforma UBP",
                "category_id": "education",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(subject_price),
            }
        ],
        "payer": {
            "email": user_email,
        },
        "back_urls": {
            "success": f"{FRONTEND_URL}?mp_status=approved&subject_id={subject_id}",
            "failure": f"{FRONTEND_URL}?mp_status=rejected&subject_id={subject_id}",
            "pending": f"{FRONTEND_URL}?mp_status=pending&subject_id={subject_id}",
        },
        "auto_return": "approved",
        "external_reference": external_reference,
        "statement_descriptor": "UBP Academia",
        "notification_url": None,  # Para producción, agregar URL de webhook
    }
    
    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        return {
            "id": preference["id"],
            "init_point": preference.get("init_point"),
            "sandbox_init_point": preference.get("sandbox_init_point"),
            "external_reference": external_reference,
            "simulation": False,
        }
    except Exception as e:
        print(f"❌ Error creando preferencia MP: {e}")
        # Fallback a simulación si falla
        return {
            "id": f"sim_{uuid.uuid4().hex[:12]}",
            "init_point": None,
            "sandbox_init_point": None,
            "external_reference": external_reference,
            "simulation": True,
            "preference_data": {
                "title": subject_title,
                "price": subject_price,
                "currency": "ARS",
                "subject_id": subject_id,
                "user_id": user_id,
            }
        }


def process_payment_notification(payment_id: str) -> Dict[str, Any]:
    """
    Procesa una notificación de pago de MercadoPago.
    En modo simulación, retorna datos simulados como aprobado.
    """
    if SIMULATION_MODE:
        return {
            "id": payment_id,
            "status": "approved",
            "status_detail": "accredited",
            "payment_method": "credit_card",
            "payment_type": "credit_card",
            "transaction_amount": 0,
            "simulation": True,
        }
    
    sdk = get_mp_sdk()
    if not sdk:
        raise Exception("No se pudo inicializar MercadoPago SDK")
    
    try:
        payment_info = sdk.payment().get(payment_id)
        return payment_info["response"]
    except Exception as e:
        print(f"❌ Error obteniendo info de pago: {e}")
        raise


def get_payment_status_label(status: str) -> str:
    """Retorna la etiqueta en español del estado del pago"""
    labels = {
        "approved": "Aprobado",
        "pending": "Pendiente",
        "in_process": "En proceso",
        "rejected": "Rechazado",
        "cancelled": "Cancelado",
        "refunded": "Reembolsado",
    }
    return labels.get(status, status)


# Info del modo actual (útil para debug/presentación)
def get_mp_config_info() -> Dict[str, Any]:
    """Retorna información de la configuración de MercadoPago"""
    return {
        "simulation_mode": SIMULATION_MODE,
        "has_access_token": bool(MP_ACCESS_TOKEN),
        "has_public_key": bool(MP_PUBLIC_KEY),
        "frontend_url": FRONTEND_URL,
    }
