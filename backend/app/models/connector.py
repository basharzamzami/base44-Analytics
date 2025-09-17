from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Connector(Base):
    __tablename__ = "connectors"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    type = Column(String(50), nullable=False)  # csv, hubspot, google_ads
    credentials_encrypted = Column(Text)
    config_json = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="connectors")
    raw_ingests = relationship("RawIngest", back_populates="connector")

class RawIngest(Base):
    __tablename__ = "raw_ingest"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    raw_data = Column(JSON, nullable=False)
    status = Column(String(50), default="pending")  # pending, processed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    connector = relationship("Connector", back_populates="raw_ingests")

class NormalizedRecord(Base):
    __tablename__ = "normalized_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    raw_ingest_id = Column(Integer, ForeignKey("raw_ingest.id"), nullable=False)
    normalized_data = Column(JSON, nullable=False)
    entity_type = Column(String(100))  # customer, lead, patient, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    raw_ingest = relationship("RawIngest")
