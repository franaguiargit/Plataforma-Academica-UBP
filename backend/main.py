from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

# Imports de modelos y database
from database import get_db, engine
from models import Base, User, Subject, Content, Purchase

# Crear las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas de Pydantic
class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    full_name: str = None

class UserLogin(BaseModel):
    username: str
    password: str

class SubjectCreate(BaseModel):
    title: str
    description: str = None
    price: float

class ContentCreate(BaseModel):
    title: str
    description: str = None
    content_type: str
    content_url: str = None
    subject_id: int
    order_index: int = 1
    duration: str = None

class Token(BaseModel):
    access_token: str
    token_type: str

# Funciones de autenticación
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Obtener usuario actual del token JWT"""
    
    # Si no hay authorization header, usar admin para pruebas
    if not authorization:
        print("⚠️  No hay authorization header, usando admin por defecto")
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            raise HTTPException(status_code=401, detail="Usuario admin no encontrado")
        return admin
    
    try:
        # Extraer token del header "Bearer TOKEN"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Esquema de autorización inválido")
        
        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
            
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # Buscar usuario
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    print(f"✅ Usuario autenticado: {user.username} ({user.role})")
    return user

# Implementación simplificada de autenticación para las rutas
async def get_current_user(db: Session = Depends(get_db)):
    # Por ahora, retornamos el admin para pruebas
    # En producción, esto debe validar el JWT del header
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    return admin

# ===================================
# RUTAS BÁSICAS
# ===================================

@app.get("/")
async def root():
    return {"message": "API Plataforma Académica UBP"}

@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role="student"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Usuario creado exitosamente"}

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def read_users_me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Obtener información del usuario actual"""
    
    # Si no hay authorization header, buscar por username en la query (temporal)
    if not authorization:
        # Para compatibilidad con login simple, usar admin por defecto
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    
    try:
        # Extraer token del header "Bearer TOKEN"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Esquema de autorización inválido")
        
        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
            
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # Buscar usuario
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

# ===================================
# RUTAS DE MATERIAS
# ===================================

@app.get("/subjects")
async def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    return subjects

@app.post("/subjects")
async def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    db_subject = Subject(
        title=subject.title,
        description=subject.description,
        price=subject.price
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@app.get("/subjects/{subject_id}/content")
async def get_subject_content(subject_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.subject_id == subject_id).all()
    return content

# ===================================
# RUTAS DE CONTENIDO
# ===================================

@app.post("/content")
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_content = Content(
        title=content.title,
        description=content.description,
        type=content.content_type,
        content_url=content.content_url,
        subject_id=content.subject_id,
        order_index=content.order_index,
        duration=content.duration
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

# ===================================
# RUTAS DE COMPRAS
# ===================================

@app.post("/purchase/{subject_id}")
async def purchase_subject(subject_id: int, db: Session = Depends(get_db)):
    # Simplificado - usar usuario admin para pruebas
    user = db.query(User).filter(User.username == "admin").first()
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    # Verificar si ya compró la materia
    existing_purchase = db.query(Purchase).filter(
        Purchase.user_id == user.id,
        Purchase.subject_id == subject_id
    ).first()
    
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Ya compraste esta materia")
    
    # Crear compra
    purchase = Purchase(
        user_id=user.id,
        subject_id=subject_id,
        amount=subject.price
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    
    return {"message": "Compra realizada exitosamente"}

@app.get("/my-purchases")
async def get_my_purchases(db: Session = Depends(get_db)):
    # Simplificado - usar usuario admin
    user = db.query(User).filter(User.username == "admin").first()
    purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()
    return purchases

# ===================================
# RUTAS DE ADMINISTRACIÓN
# ===================================

@app.get("/admin/users")
async def get_all_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtener todos los usuarios (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    users = db.query(User).filter(User.role == "student").all()
    
    # Calcular estadísticas para cada usuario
    users_data = []
    for user in users:
        purchases = db.query(Purchase).filter(Purchase.user_id == user.id).all()
        subjects_purchased = len(purchases)
        total_spent = sum(purchase.amount for purchase in purchases)
        
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name or user.username,
            "subjects_purchased": subjects_purchased,
            "total_spent": float(total_spent),
            "last_access": user.created_at.isoformat(),
            "status": "active"
        })
    
    return users_data

@app.get("/admin/stats")
async def get_admin_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtener estadísticas generales"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    total_users = db.query(User).filter(User.role == "student").count()
    total_subjects = db.query(Subject).count()
    total_purchases = db.query(Purchase).count()
    total_revenue = db.query(func.sum(Purchase.amount)).scalar() or 0
    
    return {
        "total_students": total_users,
        "total_subjects": total_subjects,
        "total_purchases": total_purchases,
        "total_revenue": float(total_revenue),
        "active_today": max(1, total_users // 3),
        "students_with_purchases": db.query(Purchase.user_id).distinct().count()
    }

@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Eliminar materia (solo admin)"""
    print(f"🗑️ Intentando eliminar materia ID: {subject_id}")
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    # Buscar la materia
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        print(f"❌ Materia {subject_id} no encontrada")
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    print(f"✅ Materia encontrada: {subject.title}")
    
    # Verificar si hay compras asociadas
    purchases_count = db.query(Purchase).filter(Purchase.subject_id == subject_id).count()
    print(f"📊 Compras asociadas: {purchases_count}")
    
    if purchases_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la materia porque tiene {purchases_count} compra(s) asociada(s). Las compras realizadas deben mantenerse para los estudiantes."
        )
    
    try:
        # Eliminar contenido asociado primero
        contents_deleted = db.query(Content).filter(Content.subject_id == subject_id).delete()
        print(f"🗑️ Contenidos eliminados: {contents_deleted}")
        
        # Eliminar materia
        db.delete(subject)
        db.commit()
        
        print(f"✅ Materia {subject.title} eliminada exitosamente")
        
        return {"message": f"Materia '{subject.title}' eliminada exitosamente"}
        
    except Exception as e:
        print(f"❌ Error eliminando materia: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.delete("/content/{content_id}")
async def delete_content(content_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Eliminar contenido (solo admin)"""
    print(f"🗑️ Intentando eliminar contenido ID: {content_id}")
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    # Buscar el contenido
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        print(f"❌ Contenido {content_id} no encontrado")
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    print(f"✅ Contenido encontrado: {content.title}")
    
    try:
        # Eliminar contenido
        db.delete(content)
        db.commit()
        
        print(f"✅ Contenido {content.title} eliminado exitosamente")
        
        return {"message": f"Contenido '{content.title}' eliminado exitosamente"}
        
    except Exception as e:
        print(f"❌ Error eliminando contenido: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/subjects/{subject_id}/purchases")
async def get_subject_purchases(subject_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtener compras de una materia específica"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    purchases = db.query(Purchase).filter(Purchase.subject_id == subject_id).join(User).all()
    
    return [{
        "id": purchase.id,
        "user_id": purchase.user_id,
        "username": purchase.user.username,
        "full_name": purchase.user.full_name or purchase.user.username,
        "amount": float(purchase.amount),
        "created_at": purchase.created_at.isoformat()
    } for purchase in purchases]

@app.put("/subjects/{subject_id}")
async def update_subject(subject_id: int, subject: SubjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Actualizar materia (solo admin)"""
    print(f"📝 Intentando actualizar materia ID: {subject_id}")
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    
    # Buscar la materia
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        print(f"❌ Materia {subject_id} no encontrada")
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    print(f"✅ Materia encontrada: {db_subject.title}")
    
    try:
        # Actualizar campos
        db_subject.title = subject.title
        db_subject.description = subject.description
        db_subject.price = subject.price
        
        db.commit()
        db.refresh(db_subject)
        
        print(f"✅ Materia actualizada: {db_subject.title}")
        
        return db_subject
        
    except Exception as e:
        print(f"❌ Error actualizando materia: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# AGREGAR esta ruta temporal para crear usuarios:
@app.post("/init-users")
async def init_users(db: Session = Depends(get_db)):
    """Crear usuarios iniciales"""
    
    # Verificar si admin existe
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@ubp.edu.ar",
            full_name="Administrador",
            hashed_password=get_password_hash("admin"),
            role="admin"
        )
        db.add(admin)
    
    # Verificar si fran existe
    fran = db.query(User).filter(User.username == "fran").first()
    if not fran:
        fran = User(
            username="fran",
            email="fran@estudiante.ubp.edu.ar",
            full_name="Francisco García",
            hashed_password=get_password_hash("secret"),
            role="student"
        )
        db.add(fran)
    
    db.commit()
    
    return {"message": "Usuarios inicializados correctamente"}