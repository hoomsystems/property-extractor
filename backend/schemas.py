from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

class RealEstateAgentBase(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = {}
    internal_contact: Optional[str] = None

class RealEstateAgentCreate(RealEstateAgentBase):
    pass

class RealEstateAgentResponse(RealEstateAgentBase):
    id: int

    class Config:
        orm_mode = True

class PropertyCreate(BaseModel):
    title: str
    price: str
    location: str
    url: str
    description: Optional[str] = None
    notes: Optional[str] = None
    images: List[str] = []
    main_image: Optional[str] = None
    
    # Dimensiones
    lot_size: Optional[float] = None
    construction_size: Optional[float] = None
    
    # Características numéricas
    bathrooms: Optional[float] = None
    bedrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    floors: Optional[int] = None
    
    # Estado de la propiedad
    is_new: bool = False
    
    # Características detalladas
    general_features: List[str] = []
    services: List[str] = []
    exterior_features: List[str] = []
    
    # Agente inmobiliario
    agent: Optional[RealEstateAgentCreate] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyUpdate(PropertyCreate):
    pass

class PropertyResponse(PropertyCreate):
    id: int
    date: datetime
    agent: Optional[RealEstateAgentResponse] = None

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    items: List[PropertyResponse]
    total_items: int
    total_pages: int
    current_page: int
    per_page: int 