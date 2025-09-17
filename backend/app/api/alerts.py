from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.alert import Alert
from app.models.user import User
from app.services.alert_engine import alert_engine
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertResponse(BaseModel):
    id: int
    tenant_id: int
    kpi_id: Optional[int]
    rule_json: dict
    severity: str
    triggered_at: datetime
    resolved_at: Optional[datetime]
    details: dict
    acknowledged: bool
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]


class AcknowledgeRequest(BaseModel):
    acknowledged: bool = True


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all alerts for the tenant"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    alerts = db.query(Alert).filter(
        Alert.tenant_id == int(x_tenant_id)
    ).order_by(Alert.triggered_at.desc()).all()
    
    return [
        AlertResponse(
            id=alert.id,
            tenant_id=alert.tenant_id,
            kpi_id=alert.kpi_id,
            rule_json=alert.rule_json,
            severity=alert.severity,
            triggered_at=alert.triggered_at,
            resolved_at=alert.resolved_at,
            details=alert.details,
            acknowledged=alert.acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at
        )
        for alert in alerts
    ]


@router.post("/{alert_id}/ack")
async def acknowledge_alert(
    alert_id: int,
    request: AcknowledgeRequest,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == int(x_tenant_id)
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.acknowledged = request.acknowledged
    if request.acknowledged:
        alert.acknowledged_by = current_user.id
        alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Alert {alert_id} {'acknowledged' if request.acknowledged else 'unacknowledged'} successfully"
    }


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == int(x_tenant_id)
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": f"Alert {alert_id} resolved successfully"
    }


@router.post("/generate-mock")
async def generate_mock_alerts(
    vertical: str = "marketing_agency",
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate mock alerts for demo purposes"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    try:
        # Generate mock alerts
        mock_alerts = alert_engine.generate_mock_alerts(int(x_tenant_id), vertical)
        
        # Save alerts to database
        for alert in mock_alerts:
            db.add(alert)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Generated {len(mock_alerts)} mock alerts",
            "alerts_created": len(mock_alerts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate mock alerts: {str(e)}"
        )

