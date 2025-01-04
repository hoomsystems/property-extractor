from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.models import Base, RealEstateAgent, Property
from backend.database import engine
import backend.routes as routes
import os

# Eliminar la base de datos si existe (solo durante desarrollo)
#if os.path.exists("properties.db"):
#    os.remove("properties.db")

# Crear todas las tablas
print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas exitosamente")

app = FastAPI(title="Property Collector API")

# Configurar CORS de manera más permisiva
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8501",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8501",
    "https://www.inmuebles24.com",
    "https://inmuebles24.com",
    "*"  # Permitir todos los orígenes
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# Middleware para manejar errores CORS
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PUT, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# Manejador de errores
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, DELETE, PUT, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

# Asegurarnos de que el directorio static existe
os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir rutas
app.include_router(routes.router)

# Ruta para verificar que collector.js es accesible
@app.get("/test-collector")
async def test_collector():
    return FileResponse("static/collector.js")

# Ruta OPTIONS para preflight requests
@app.options("/{path:path}")
async def options_handler(request: Request):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, DELETE, PUT, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    ) 