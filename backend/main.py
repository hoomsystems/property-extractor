from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

from .routes import router

app = FastAPI()
app.include_router(router) 