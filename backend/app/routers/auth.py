from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.utils.security import verify_password
from app.utils.jwt import create_access_token, create_refresh_token, decode_access_token, decode_token
from app.models.refresh_token import RefreshToken

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ========= DEPENDENCIAS DE AUTENTICACIÓN =========

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Obtiene el usuario actual a partir del token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # En tu implementación original, el 'sub' es el USERNAME, no el ID
    username = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_admin_or_teacher(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Verifica que el usuario actual sea admin o teacher.
    """
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )
    return current_user


# ========= ENDPOINTS =========

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login: devuelve access_token + datos básicos del usuario.
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    # En tu modelo el campo es 'hashed_password'
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear access token y refresh token
    access_token = create_access_token(user.username)
    refresh_tok, jti, expires_at = create_refresh_token(user.username)

    # Guardar refresh token en DB
    db_refresh = RefreshToken(
        token=refresh_tok,
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_tok,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/refresh")
def refresh_access_token(
    db: Session = Depends(get_db),
):
    """
    Renueva el access_token usando un refresh_token enviado en el body.
    """
    from fastapi import Request
    import json
    # We need the raw body, but since this is tricky, let's use a Pydantic model
    pass


from pydantic import BaseModel as _BM

class _RefreshRequest(_BM):
    refresh_token: str

@router.post("/refresh-token")
def refresh_token_endpoint(
    body: _RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Renueva el access_token usando un refresh_token.
    """
    from jose import JWTError
    try:
        payload = decode_token(body.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token no es de tipo refresh")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar que el refresh token no esté revocado
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == body.refresh_token,
        RefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token revocado o no encontrado")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # Crear nuevo access token
    new_access_token = create_access_token(user.username)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Devuelve el usuario autenticado.
    """
    return current_user