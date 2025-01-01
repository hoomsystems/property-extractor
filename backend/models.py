from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RealEstateAgent(Base):
    __tablename__ = "real_estate_agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    social_media = Column(JSON, default=dict)
    internal_contact = Column(String, nullable=True)
    properties = relationship("Property", back_populates="agent")

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(String)
    location = Column(String)
    url = Column(String)
    description = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    images = Column(JSON, default=list)
    main_image = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Dimensiones
    lot_size = Column(Float, nullable=True)
    construction_size = Column(Float, nullable=True)
    
    # Características numéricas
    bathrooms = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    parking_spaces = Column(Integer, nullable=True)
    floors = Column(Integer, nullable=True)
    
    # Estado de la propiedad
    is_new = Column(Boolean, default=False)
    
    # Características detalladas
    general_features = Column(JSON, default=list)
    services = Column(JSON, default=list)
    exterior_features = Column(JSON, default=list)
    
    # Relación con el agente inmobiliario
    agent_id = Column(Integer, ForeignKey("real_estate_agents.id"), nullable=True)
    agent = relationship("RealEstateAgent", back_populates="properties")
    
    # Campos para ubicación en mapa
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True) 