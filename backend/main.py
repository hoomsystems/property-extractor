from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router  # Importar el router

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Incluir el router
app.include_router(router, prefix="/api") 