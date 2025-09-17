from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.connector import Connector, RawIngest
from app.models.user import User
from app.services.csv_connector import csv_connector
from app.services.live_connectors import live_connector_service
from app.services.llm_service import llm_service
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/v1/connectors", tags=["connectors"])


class ConnectorCreate(BaseModel):
    type: str
    credentials_encrypted: Optional[str] = None
    config_json: dict = {}


class ConnectorResponse(BaseModel):
    id: int
    tenant_id: int
    type: str
    config_json: dict
    last_sync_at: Optional[datetime]
    created_at: datetime


class SyncResponse(BaseModel):
    success: bool
    records_ingested: int
    message: str


class MappingResponse(BaseModel):
    suggested_mappings: List[dict]
    confidence_threshold: float
    total_fields: int
    mapped_fields: int


@router.post("/", response_model=ConnectorResponse)
async def create_connector(
    connector: ConnectorCreate,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new connector"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    db_connector = Connector(
        tenant_id=int(x_tenant_id),
        type=connector.type,
        credentials_encrypted=connector.credentials_encrypted,
        config_json=connector.config_json
    )
    
    db.add(db_connector)
    db.commit()
    db.refresh(db_connector)
    
    return ConnectorResponse(
        id=db_connector.id,
        tenant_id=db_connector.tenant_id,
        type=db_connector.type,
        config_json=db_connector.config_json,
        last_sync_at=db_connector.last_sync_at,
        created_at=db_connector.created_at
    )


@router.get("/", response_model=List[ConnectorResponse])
async def list_connectors(
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all connectors for the tenant"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    connectors = db.query(Connector).filter(Connector.tenant_id == int(x_tenant_id)).all()
    
    return [
        ConnectorResponse(
            id=connector.id,
            tenant_id=connector.tenant_id,
            type=connector.type,
            config_json=connector.config_json,
            last_sync_at=connector.last_sync_at,
            created_at=connector.created_at
        )
        for connector in connectors
    ]


@router.post("/{connector_id}/sync", response_model=SyncResponse)
async def sync_connector(
    connector_id: int,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a sync for a connector"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    connector = db.query(Connector).filter(
        Connector.id == connector_id,
        Connector.tenant_id == int(x_tenant_id)
    ).first()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    try:
        if connector.type == "csv":
            # CSV sync is handled via file upload
            return SyncResponse(
                success=True,
                records_ingested=0,
                message="CSV sync requires file upload"
            )
        elif connector.type in ["hubspot", "google_ads"]:
            # Live connector sync
            raw_ingests = live_connector_service.sync_connector(connector, int(x_tenant_id))
            
            # Save raw ingest records
            for raw_ingest in raw_ingests:
                db.add(raw_ingest)
            
            db.commit()
            
            total_records = sum(len(ri.payload_json.get("data", [])) for ri in raw_ingests)
            
            return SyncResponse(
                success=True,
                records_ingested=total_records,
                message=f"Sync completed: {total_records} records ingested"
            )
        else:
            return SyncResponse(
                success=False,
                records_ingested=0,
                message="Unsupported connector type"
            )
    
    except Exception as e:
        return SyncResponse(
            success=False,
            records_ingested=0,
            message=f"Sync failed: {str(e)}"
        )


@router.post("/{connector_id}/upload-csv")
async def upload_csv(
    connector_id: int,
    file: UploadFile = File(...),
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process CSV file"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    connector = db.query(Connector).filter(
        Connector.id == connector_id,
        Connector.tenant_id == int(x_tenant_id)
    ).first()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    if connector.type != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connector is not a CSV connector"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process CSV
        result = csv_connector.process_csv_upload(file_content, connector, int(x_tenant_id))
        
        if result["success"]:
            # Store raw ingest record
            raw_ingest = RawIngest(
                tenant_id=int(x_tenant_id),
                connector_id=connector_id,
                payload_json={
                    "data": result["sample_data"],
                    "metadata": {
                        "file_name": file.filename,
                        "file_size": len(file_content),
                        "record_count": result["records_processed"],
                        "processed_at": datetime.utcnow().isoformat()
                    }
                }
            )
            db.add(raw_ingest)
            db.commit()
            
            return {
                "success": True,
                "message": f"CSV uploaded successfully: {result['records_processed']} records processed",
                "mapping_suggestions": result["mapping_suggestions"],
                "raw_ingest_id": raw_ingest.id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV upload failed: {str(e)}"
        )


@router.get("/{connector_id}/map_preview", response_model=MappingResponse)
async def get_map_preview(
    connector_id: int,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LLM-suggested field mapping for a connector"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    connector = db.query(Connector).filter(
        Connector.id == connector_id,
        Connector.tenant_id == int(x_tenant_id)
    ).first()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Get mapping suggestions from LLM service
    mapping_suggestions = llm_service.suggest_field_mapping(
        connector_type=connector.type,
        vertical="marketing_agency",  # Default vertical
        sample_data={}
    )
    
    return MappingResponse(
        suggested_mappings=mapping_suggestions["suggested_mappings"],
        confidence_threshold=mapping_suggestions["confidence_threshold"],
        total_fields=mapping_suggestions["total_fields"],
        mapped_fields=mapping_suggestions["mapped_fields"]
    )

