from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import List, Optional
import shutil
import os
from datetime import datetime
from backend.database import get_db
from backend.models import Property, RealEstateAgent
from backend.schemas import PropertyCreate, PropertyUpdate, PropertyResponse, PaginatedResponse, RealEstateAgentCreate, RealEstateAgentResponse

router = APIRouter()

# Crear directorio para imágenes si no existe
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/api/properties", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, db: Session = Depends(get_db)):
    # Crear o actualizar agente inmobiliario si existe información
    agent_id = None
    if property_data.agent:
        agent = db.query(RealEstateAgent).filter(
            RealEstateAgent.email == property_data.agent.email
        ).first() if property_data.agent.email else None

        if not agent:
            agent = RealEstateAgent(**property_data.agent.dict())
            db.add(agent)
            db.commit()
            db.refresh(agent)
        
        agent_id = agent.id

    # Crear la propiedad
    property_dict = property_data.dict(exclude={'agent'})
    property_dict['agent_id'] = agent_id
    
    db_property = Property(**property_dict)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@router.get("/api/properties", response_model=PaginatedResponse)
def get_properties(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None,
    sort_by: Optional[str] = "date_desc",
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    try:
        print("\n=== Iniciando get_properties ===")
        
        # Hacer un query simple primero para verificar
        query = db.query(Property)
        
        # Imprimir todas las propiedades para debug
        all_properties = query.all()
        print(f"Propiedades en la base de datos:")
        for p in all_properties:
            print(f"ID: {p.id}, Título: {p.title}, Fecha: {p.date}")
        
        # Calcular total de registros
        total_items = query.count()
        print(f"Total items encontrados: {total_items}")
        
        # Aplicar ordenamiento
        if sort_by == "date_desc":
            query = query.order_by(Property.date.desc())
        elif sort_by == "date_asc":
            query = query.order_by(Property.date.asc())
        
        # Aplicar paginación
        offset = (page - 1) * per_page
        properties = query.offset(offset).limit(per_page).all()
        
        # Imprimir propiedades que se van a devolver
        print(f"Propiedades a devolver:")
        for p in properties:
            print(f"ID: {p.id}, Título: {p.title}")
        
        response_data = {
            "items": properties,
            "total_items": total_items,
            "total_pages": max((total_items + per_page - 1) // per_page, 1),
            "current_page": page,
            "per_page": per_page
        }
        
        print("=== Finalizando get_properties ===\n")
        return response_data

    except Exception as e:
        print(f"Error en get_properties: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/api/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    # Actualizar información del agente si existe
    if property_data.agent:
        if property.agent_id:
            agent = db.query(RealEstateAgent).filter(RealEstateAgent.id == property.agent_id).first()
            for key, value in property_data.agent.dict(exclude_unset=True).items():
                setattr(agent, key, value)
        else:
            agent = RealEstateAgent(**property_data.agent.dict())
            db.add(agent)
            db.commit()
            property.agent_id = agent.id

    # Actualizar la propiedad
    property_dict = property_data.dict(exclude={'agent'}, exclude_unset=True)
    for key, value in property_dict.items():
        setattr(property, key, value)
    
    db.commit()
    db.refresh(property)
    return property

@router.delete("/api/properties/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    
    # Eliminar imágenes asociadas
    if property.images:
        for image_url in property.images:
            try:
                image_path = os.path.join("static", image_url.split("/static/")[1])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error eliminando imagen: {e}")
    
    db.delete(property)
    db.commit()
    return {"message": "Propiedad eliminada"}

@router.post("/api/properties/{property_id}/images")
async def upload_images(
    property_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    uploaded_images = []
    for file in files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{property_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        image_url = f"/static/uploads/{filename}"
        uploaded_images.append(image_url)

    # Actualizar lista de imágenes de la propiedad
    if not property.images:
        property.images = []
    property.images.extend(uploaded_images)
    db.commit()

    return {"uploaded_images": uploaded_images}

# Endpoints para vendedores
@router.post("/api/agents", response_model=RealEstateAgentResponse)
async def create_agent(agent_data: RealEstateAgentCreate, db: Session = Depends(get_db)):
    agent = RealEstateAgent(**agent_data.dict())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@router.get("/api/agents", response_model=List[RealEstateAgentResponse])
def get_agents(db: Session = Depends(get_db)):
    return db.query(RealEstateAgent).all()

@router.put("/api/agents/{agent_id}", response_model=RealEstateAgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: RealEstateAgentCreate,
    db: Session = Depends(get_db)
):
    agent = db.query(RealEstateAgent).filter(RealEstateAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    for key, value in agent_data.dict().items():
        setattr(agent, key, value)
    
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/api/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(RealEstateAgent).filter(RealEstateAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    db.delete(agent)
    db.commit()
    return {"message": "Vendedor eliminado"}

@router.get("/api/properties/check_url")
def check_property_url(url: str, db: Session = Depends(get_db)):
    property = db.query(Property).filter(Property.url == url).first()
    return {"exists": property is not None} 