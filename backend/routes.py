from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter()

class Agent(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class Property(BaseModel):
    url: str
    title: str
    location: str
    description: str
    rooms: Optional[int] = None
    bathrooms: Optional[float] = None
    construction: Optional[float] = None
    land: Optional[float] = None

@router.post("/properties")
async def create_property(property: Property):
    try:
        # Aquí iría la lógica para guardar en la base de datos
        return {"status": "success", "message": "Propiedad guardada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 