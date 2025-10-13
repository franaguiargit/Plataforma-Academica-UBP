from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.routers import auth, users, subjects, content, purchases

# Crear la aplicación
app = FastAPI(
    title="Plataforma Académica UBP",
    description="API para plataforma educativa",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(subjects.router)
app.include_router(content.router)
app.include_router(purchases.router)

@app.get("/")
def read_root():
    return {"message": "Plataforma Académica UBP API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}