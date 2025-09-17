from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.kpi import KPIDefinition, KPIValue
from app.models.user import User
from app.services.kpi_engine import kpi_engine
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/kpis", tags=["kpis"])


class KPIDefinitionCreate(BaseModel):
    name: str
    vertical: str
    formula_json: dict
    window: str = "daily"


class KPIDefinitionResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    vertical: str
    formula_json: dict
    window: str
    created_at: datetime


class KPIValueResponse(BaseModel):
    id: int
    kpi_id: int
    timestamp: datetime
    value: float
    provenance: dict


class EvaluateRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@router.get("/", response_model=List[KPIDefinitionResponse])
async def list_kpis(
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all KPI definitions for the tenant"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    kpis = db.query(KPIDefinition).filter(KPIDefinition.tenant_id == int(x_tenant_id)).all()
    
    return [
        KPIDefinitionResponse(
            id=kpi.id,
            tenant_id=kpi.tenant_id,
            name=kpi.name,
            vertical=kpi.vertical,
            formula_json=kpi.formula_json,
            window=kpi.window,
            created_at=kpi.created_at
        )
        for kpi in kpis
    ]


@router.post("/", response_model=KPIDefinitionResponse)
async def create_kpi(
    kpi: KPIDefinitionCreate,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new KPI definition"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    db_kpi = KPIDefinition(
        tenant_id=int(x_tenant_id),
        name=kpi.name,
        vertical=kpi.vertical,
        formula_json=kpi.formula_json,
        window=kpi.window
    )
    
    db.add(db_kpi)
    db.commit()
    db.refresh(db_kpi)
    
    return KPIDefinitionResponse(
        id=db_kpi.id,
        tenant_id=db_kpi.tenant_id,
        name=db_kpi.name,
        vertical=db_kpi.vertical,
        formula_json=db_kpi.formula_json,
        window=db_kpi.window,
        created_at=db_kpi.created_at
    )


@router.post("/{kpi_id}/evaluate")
async def evaluate_kpi(
    kpi_id: int,
    request: EvaluateRequest,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate/compute KPI values"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    kpi = db.query(KPIDefinition).filter(
        KPIDefinition.id == kpi_id,
        KPIDefinition.tenant_id == int(x_tenant_id)
    ).first()
    
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found"
        )
    
    try:
        # Get normalized records for KPI calculation
        from app.models.connector import NormalizedRecord
        normalized_records = db.query(NormalizedRecord).filter(
            NormalizedRecord.tenant_id == int(x_tenant_id)
        ).all()
        
        # Calculate KPI using engine
        end_date = request.end_date or datetime.utcnow()
        start_date = request.start_date or (end_date - timedelta(days=30))
        
        kpi_value = kpi_engine.calculate_kpi(kpi, normalized_records, start_date, end_date)
        
        # Save KPI value
        db.add(kpi_value)
        db.commit()
        db.refresh(kpi_value)
        
        return {
            "success": True,
            "kpi_value": KPIValueResponse(
                id=kpi_value.id,
                kpi_id=kpi_value.kpi_id,
                timestamp=kpi_value.timestamp,
                value=kpi_value.value,
                provenance=kpi_value.provenance
            ),
            "message": f"KPI '{kpi.name}' evaluated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"KPI evaluation failed: {str(e)}"
        )


@router.get("/{kpi_id}/values", response_model=List[KPIValueResponse])
async def get_kpi_values(
    kpi_id: int,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get KPI values for a specific KPI"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    # Verify KPI belongs to tenant
    kpi = db.query(KPIDefinition).filter(
        KPIDefinition.id == kpi_id,
        KPIDefinition.tenant_id == int(x_tenant_id)
    ).first()
    
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found"
        )
    
    values = db.query(KPIValue).filter(
        KPIValue.kpi_id == kpi_id,
        KPIValue.tenant_id == int(x_tenant_id)
    ).order_by(KPIValue.timestamp.desc()).limit(100).all()
    
    return [
        KPIValueResponse(
            id=value.id,
            kpi_id=value.kpi_id,
            timestamp=value.timestamp,
            value=value.value,
            provenance=value.provenance
        )
        for value in values
    ]

