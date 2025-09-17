from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.kpi import KPIDefinition, KPIValue
from app.models.alert import Alert, Task
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class DashboardTile(BaseModel):
    id: str
    type: str  # kpi, alert, chart, table
    title: str
    data: Dict[Any, Any]
    position: Dict[str, int]  # x, y, width, height


class DashboardResponse(BaseModel):
    tenant_id: int
    tiles: List[DashboardTile]
    last_updated: datetime


@router.get("/{tenant_id}", response_model=DashboardResponse)
async def get_dashboard(
    tenant_id: int,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for a tenant"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, str(tenant_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    # Verify header matches
    if str(tenant_id) != x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header mismatch"
        )
    
    # Get KPIs
    kpis = db.query(KPIDefinition).filter(KPIDefinition.tenant_id == tenant_id).all()
    
    # Get latest KPI values
    kpi_tiles = []
    for i, kpi in enumerate(kpis):
        latest_value = db.query(KPIValue).filter(
            KPIValue.kpi_id == kpi.id
        ).order_by(KPIValue.timestamp.desc()).first()
        
        kpi_tiles.append(DashboardTile(
            id=f"kpi_{kpi.id}",
            type="kpi",
            title=kpi.name,
            data={
                "value": latest_value.value if latest_value else 0,
                "trend": "up" if latest_value and latest_value.value > 50 else "down",
                "unit": "%" if "rate" in kpi.name.lower() else "count"
            },
            position={"x": (i % 2) * 6, "y": (i // 2) * 4, "width": 6, "height": 4}
        ))
    
    # Get active alerts
    active_alerts = db.query(Alert).filter(
        Alert.tenant_id == tenant_id,
        Alert.resolved_at.is_(None)
    ).order_by(Alert.triggered_at.desc()).limit(5).all()
    
    alert_tiles = [
        DashboardTile(
            id=f"alert_{alert.id}",
            type="alert",
            title=f"Alert: {alert.rule_json.get('name', 'Unknown')}",
            data={
                "severity": alert.severity,
                "triggered_at": alert.triggered_at.isoformat(),
                "details": alert.details
            },
            position={"x": 0, "y": 8, "width": 12, "height": 3}
        )
        for alert in active_alerts
    ]
    
    # Get recent tasks
    recent_tasks = db.query(Task).filter(
        Task.tenant_id == tenant_id
    ).order_by(Task.created_at.desc()).limit(5).all()
    
    task_tiles = [
        DashboardTile(
            id=f"task_{task.id}",
            type="table",
            title="Recent Tasks",
            data={
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status,
                        "assigned_to": task.assigned_to,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in recent_tasks
                ]
            },
            position={"x": 0, "y": 12, "width": 12, "height": 4}
        )
    ]
    
    # Combine all tiles
    all_tiles = kpi_tiles + alert_tiles + task_tiles
    
    return DashboardResponse(
        tenant_id=tenant_id,
        tiles=all_tiles,
        last_updated=datetime.utcnow()
    )

