from app.database import engine, Base
from app import models  # Importa todos los modelos para crear las tablas

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI

app = FastAPI(
    title="Plataforma Académica UBP",
    description="API para material académico de Ingeniería en Informática",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la Plataforma Académica UBP"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)