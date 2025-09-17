from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.tenant import Tenant
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])

class TenantResponse(BaseModel):
    id: int
    name: str
    plan: str
    config_json: dict
    is_active: bool
    created_at: str

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    x_tenant_id: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tenant information"""
    # Verify tenant access
    if not verify_tenant_access(current_user, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        plan=tenant.plan,
        config_json=tenant.config_json,
        is_active=tenant.is_active,
        created_at=tenant.created_at.isoformat()
    )