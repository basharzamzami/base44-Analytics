from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.kpi import KPIDefinition, KPIValue
from app.models.alert import Prediction
from app.models.user import User
from app.services.forecasting_service import forecasting_service
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


class ForecastRequest(BaseModel):
    kpi_id: int
    forecast_days: int = 30
    method: str = "prophet"  # prophet, trend, ensemble


class PredictionResponse(BaseModel):
    id: int
    tenant_id: int
    model_name: str
    input_snapshot: dict
    output_json: dict
    created_at: datetime


@router.post("/run", response_model=PredictionResponse)
async def run_forecast(
    request: ForecastRequest,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run forecasting for a KPI"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    # Get KPI definition
    kpi = db.query(KPIDefinition).filter(
        KPIDefinition.id == request.kpi_id,
        KPIDefinition.tenant_id == int(x_tenant_id)
    ).first()
    
    if not kpi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found"
        )
    
    # Get historical KPI values
    kpi_values = db.query(KPIValue).filter(
        KPIValue.kpi_id == request.kpi_id,
        KPIValue.tenant_id == int(x_tenant_id)
    ).order_by(KPIValue.timestamp.desc()).limit(90).all()
    
    # Generate forecast
    if request.method == "ensemble":
        prediction = forecasting_service.generate_ensemble_forecast(
            kpi_values, kpi, request.forecast_days
        )
    else:
        prediction = forecasting_service.generate_forecast(
            kpi_values, kpi, request.forecast_days
        )
    
    # Save prediction to database
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return PredictionResponse(
        id=prediction.id,
        tenant_id=prediction.tenant_id,
        model_name=prediction.model_name,
        input_snapshot=prediction.input_snapshot,
        output_json=prediction.output_json,
        created_at=prediction.created_at
    )


@router.get("/", response_model=List[PredictionResponse])
async def list_predictions(
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all predictions for the tenant"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    predictions = db.query(Prediction).filter(
        Prediction.tenant_id == int(x_tenant_id)
    ).order_by(Prediction.created_at.desc()).limit(50).all()
    
    return [
        PredictionResponse(
            id=prediction.id,
            tenant_id=prediction.tenant_id,
            model_name=prediction.model_name,
            input_snapshot=prediction.input_snapshot,
            output_json=prediction.output_json,
            created_at=prediction.created_at
        )
        for prediction in predictions
    ]


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific prediction"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.tenant_id == int(x_tenant_id)
    ).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    return PredictionResponse(
        id=prediction.id,
        tenant_id=prediction.tenant_id,
        model_name=prediction.model_name,
        input_snapshot=prediction.input_snapshot,
        output_json=prediction.output_json,
        created_at=prediction.created_at
    )

