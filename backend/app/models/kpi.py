from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class KPIDefinition(Base):
    __tablename__ = "kpi_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    formula = Column(Text, nullable=False)  # SQL or calculation formula
    target_value = Column(Float)
    alert_threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    values = relationship("KPIValue", back_populates="kpi_definition")

class KPIValue(Base):
    __tablename__ = "kpi_values"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    kpi_definition_id = Column(Integer, ForeignKey("kpi_definitions.id"), nullable=False)
    value = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON, default={})
    
    # Relationships
    kpi_definition = relationship("KPIDefinition", back_populates="values")
