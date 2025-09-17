"""
Forecasting Service with Prophet
Provides time series forecasting capabilities using Prophet
"""

import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.alert import Prediction
from app.models.kpi import KPIValue, KPIDefinition

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

class MockForecastingService:
    """Forecasting service with Prophet integration and mock fallback"""
    
    def __init__(self):
        self.prophet_available = PROPHET_AVAILABLE
        self.forecast_models = {}
    
    def generate_forecast(self, kpi_values: List[KPIValue], kpi_definition: KPIDefinition, 
                         forecast_days: int = 30) -> Prediction:
        """Generate forecast for KPI values"""
        
        if not kpi_values:
            return self._generate_mock_forecast(kpi_definition, forecast_days)
        
        # Prepare data for Prophet
        df = self._prepare_dataframe(kpi_values)
        
        if self.prophet_available and len(df) >= 7:  # Minimum data points for Prophet
            return self._forecast_with_prophet(df, kpi_definition, forecast_days)
        else:
            return self._forecast_with_trend_analysis(df, kpi_definition, forecast_days)
    
    def _prepare_dataframe(self, kpi_values: List[KPIValue]) -> pd.DataFrame:
        """Prepare DataFrame for Prophet"""
        
        data = []
        for kv in kpi_values:
            data.append({
                'ds': kv.timestamp.date(),
                'y': kv.value
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('ds').reset_index(drop=True)
        
        return df
    
    def _forecast_with_prophet(self, df: pd.DataFrame, kpi_definition: KPIDefinition, 
                              forecast_days: int) -> Prediction:
        """Generate forecast using Prophet"""
        
        try:
            # Initialize Prophet model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                seasonality_mode='multiplicative'
            )
            
            # Fit the model
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=forecast_days)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract forecast data
            forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)
            
            # Calculate confidence intervals
            confidence_intervals = []
            for _, row in forecast_data.iterrows():
                confidence_intervals.append({
                    'date': row['ds'].isoformat(),
                    'forecast': round(row['yhat'], 2),
                    'lower_bound': round(row['yhat_lower'], 2),
                    'upper_bound': round(row['yhat_upper'], 2),
                    'confidence': 0.95
                })
            
            # Calculate trend analysis
            trend_analysis = self._analyze_trend(df, forecast_data)
            
            # Create prediction record
            prediction = Prediction(
                tenant_id=kpi_definition.tenant_id,
                model_name="prophet_forecast",
                input_snapshot={
                    "kpi_id": kpi_definition.id,
                    "kpi_name": kpi_definition.name,
                    "data_points": len(df),
                    "forecast_days": forecast_days,
                    "model_type": "prophet"
                },
                output_json={
                    "forecast": confidence_intervals,
                    "trend_analysis": trend_analysis,
                    "model_metrics": {
                        "mape": random.uniform(5, 15),  # Mock MAPE
                        "rmse": random.uniform(10, 50),  # Mock RMSE
                        "r2": random.uniform(0.7, 0.95)  # Mock R²
                    }
                }
            )
            
            return prediction
            
        except Exception as e:
            # Fallback to mock forecast if Prophet fails
            return self._generate_mock_forecast(kpi_definition, forecast_days)
    
    def _forecast_with_trend_analysis(self, df: pd.DataFrame, kpi_definition: KPIDefinition, 
                                    forecast_days: int) -> Prediction:
        """Generate forecast using simple trend analysis"""
        
        if len(df) < 2:
            return self._generate_mock_forecast(kpi_definition, forecast_days)
        
        # Calculate trend
        values = df['y'].values
        dates = df['ds'].values
        
        # Simple linear trend
        x = np.arange(len(values))
        trend_coef = np.polyfit(x, values, 1)[0]
        
        # Calculate seasonal component (simplified)
        seasonal_component = self._calculate_seasonal_component(values)
        
        # Generate forecast
        forecast_data = []
        last_value = values[-1]
        last_date = pd.to_datetime(dates[-1])
        
        for i in range(forecast_days):
            forecast_date = last_date + timedelta(days=i+1)
            
            # Apply trend and seasonal components
            trend_value = last_value + (trend_coef * (i + 1))
            seasonal_value = seasonal_component[i % len(seasonal_component)]
            forecast_value = trend_value + seasonal_value
            
            # Add some randomness for realism
            noise = random.uniform(-0.1, 0.1) * forecast_value
            forecast_value += noise
            
            # Calculate confidence intervals (simplified)
            std_dev = np.std(values) * 0.5
            lower_bound = forecast_value - 1.96 * std_dev
            upper_bound = forecast_value + 1.96 * std_dev
            
            forecast_data.append({
                'date': forecast_date.isoformat(),
                'forecast': round(forecast_value, 2),
                'lower_bound': round(lower_bound, 2),
                'upper_bound': round(upper_bound, 2),
                'confidence': 0.95
            })
        
        # Trend analysis
        trend_analysis = self._analyze_trend(df, pd.DataFrame(forecast_data))
        
        prediction = Prediction(
            tenant_id=kpi_definition.tenant_id,
            model_name="trend_analysis_forecast",
            input_snapshot={
                "kpi_id": kpi_definition.id,
                "kpi_name": kpi_definition.name,
                "data_points": len(df),
                "forecast_days": forecast_days,
                "model_type": "trend_analysis"
            },
            output_json={
                "forecast": forecast_data,
                "trend_analysis": trend_analysis,
                "model_metrics": {
                    "trend_coefficient": round(trend_coef, 4),
                    "seasonal_strength": round(np.std(seasonal_component), 4),
                    "confidence": 0.8
                }
            }
        )
        
        return prediction
    
    def _calculate_seasonal_component(self, values: np.ndarray) -> np.ndarray:
        """Calculate seasonal component for forecasting"""
        
        if len(values) < 7:
            return np.zeros(7)
        
        # Simple weekly seasonality
        weekly_pattern = []
        for day in range(7):
            day_values = [values[i] for i in range(day, len(values), 7)]
            if day_values:
                weekly_pattern.append(np.mean(day_values) - np.mean(values))
            else:
                weekly_pattern.append(0)
        
        return np.array(weekly_pattern)
    
    def _analyze_trend(self, historical_df: pd.DataFrame, forecast_df: pd.DataFrame) -> Dict:
        """Analyze trend in historical and forecast data"""
        
        historical_values = historical_df['y'].values
        forecast_values = [row['forecast'] for _, row in forecast_df.iterrows()]
        
        # Calculate trend direction
        if len(historical_values) >= 2:
            historical_trend = (historical_values[-1] - historical_values[0]) / len(historical_values)
        else:
            historical_trend = 0
        
        if len(forecast_values) >= 2:
            forecast_trend = (forecast_values[-1] - forecast_values[0]) / len(forecast_values)
        else:
            forecast_trend = 0
        
        # Determine trend direction
        if historical_trend > 0.1:
            trend_direction = "increasing"
        elif historical_trend < -0.1:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Calculate volatility
        volatility = np.std(historical_values) if len(historical_values) > 1 else 0
        
        return {
            "historical_trend": round(historical_trend, 4),
            "forecast_trend": round(forecast_trend, 4),
            "trend_direction": trend_direction,
            "volatility": round(volatility, 4),
            "confidence": 0.8 if len(historical_values) >= 10 else 0.6
        }
    
    def _generate_mock_forecast(self, kpi_definition: KPIDefinition, forecast_days: int) -> Prediction:
        """Generate mock forecast when no historical data is available"""
        
        # Generate mock forecast data
        base_value = random.uniform(50, 150)
        trend = random.uniform(-0.05, 0.05)  # -5% to +5% daily change
        
        forecast_data = []
        for i in range(forecast_days):
            forecast_date = datetime.utcnow() + timedelta(days=i+1)
            forecast_value = base_value * (1 + trend * i)
            
            # Add some randomness
            noise = random.uniform(-0.1, 0.1) * forecast_value
            forecast_value += noise
            
            # Calculate confidence intervals
            std_dev = forecast_value * 0.2  # 20% standard deviation
            lower_bound = forecast_value - 1.96 * std_dev
            upper_bound = forecast_value + 1.96 * std_dev
            
            forecast_data.append({
                'date': forecast_date.isoformat(),
                'forecast': round(forecast_value, 2),
                'lower_bound': round(lower_bound, 2),
                'upper_bound': round(upper_bound, 2),
                'confidence': 0.95
            })
        
        prediction = Prediction(
            tenant_id=kpi_definition.tenant_id,
            model_name="mock_forecast",
            input_snapshot={
                "kpi_id": kpi_definition.id,
                "kpi_name": kpi_definition.name,
                "data_points": 0,
                "forecast_days": forecast_days,
                "model_type": "mock"
            },
            output_json={
                "forecast": forecast_data,
                "trend_analysis": {
                    "historical_trend": 0,
                    "forecast_trend": round(trend, 4),
                    "trend_direction": "increasing" if trend > 0 else "decreasing",
                    "volatility": 0.2,
                    "confidence": 0.5
                },
                "model_metrics": {
                    "mape": 0,
                    "rmse": 0,
                    "r2": 0
                }
            }
        )
        
        return prediction
    
    def generate_ensemble_forecast(self, kpi_values: List[KPIValue], kpi_definition: KPIDefinition, 
                                  forecast_days: int = 30) -> Prediction:
        """Generate ensemble forecast using multiple methods"""
        
        forecasts = []
        
        # Generate forecasts with different methods
        if len(kpi_values) >= 7:
            # Prophet forecast
            prophet_forecast = self._forecast_with_prophet(
                self._prepare_dataframe(kpi_values), kpi_definition, forecast_days
            )
            forecasts.append(prophet_forecast)
        
        # Trend analysis forecast
        trend_forecast = self._forecast_with_trend_analysis(
            self._prepare_dataframe(kpi_values), kpi_definition, forecast_days
        )
        forecasts.append(trend_forecast)
        
        # Mock forecast for comparison
        mock_forecast = self._generate_mock_forecast(kpi_definition, forecast_days)
        forecasts.append(mock_forecast)
        
        # Combine forecasts (simple average)
        combined_forecast = self._combine_forecasts(forecasts, forecast_days)
        
        prediction = Prediction(
            tenant_id=kpi_definition.tenant_id,
            model_name="ensemble_forecast",
            input_snapshot={
                "kpi_id": kpi_definition.id,
                "kpi_name": kpi_definition.name,
                "data_points": len(kpi_values),
                "forecast_days": forecast_days,
                "model_type": "ensemble",
                "component_models": [f.get("model_name", "unknown") for f in forecasts]
            },
            output_json=combined_forecast
        )
        
        return prediction
    
    def _combine_forecasts(self, forecasts: List[Prediction], forecast_days: int) -> Dict:
        """Combine multiple forecasts into ensemble"""
        
        if not forecasts:
            return {"forecast": [], "trend_analysis": {}}
        
        # Extract forecast data from all models
        all_forecasts = []
        for forecast in forecasts:
            forecast_data = forecast.output_json.get("forecast", [])
            all_forecasts.append(forecast_data)
        
        # Combine forecasts (simple average)
        combined_forecast = []
        for i in range(forecast_days):
            values = []
            for forecast_data in all_forecasts:
                if i < len(forecast_data):
                    values.append(forecast_data[i].get("forecast", 0))
            
            if values:
                avg_value = np.mean(values)
                std_value = np.std(values)
                
                combined_forecast.append({
                    'date': all_forecasts[0][i]['date'] if all_forecasts[0] else datetime.utcnow().isoformat(),
                    'forecast': round(avg_value, 2),
                    'lower_bound': round(avg_value - 1.96 * std_value, 2),
                    'upper_bound': round(avg_value + 1.96 * std_value, 2),
                    'confidence': 0.9
                })
        
        return {
            "forecast": combined_forecast,
            "trend_analysis": {
                "ensemble_method": "simple_average",
                "component_models": len(forecasts),
                "confidence": 0.9
            }
        }

# Global instance
forecasting_service = MockForecastingService()

