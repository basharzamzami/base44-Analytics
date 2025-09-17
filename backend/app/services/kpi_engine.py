"""
KPI Calculation Engine with Mock Data
Calculates KPIs based on normalized records and predefined formulas
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.kpi import KPIDefinition, KPIValue
from app.models.connector import NormalizedRecord

class MockKPIEngine:
    """Mock KPI calculation engine for demo purposes"""
    
    def __init__(self):
        self.kpi_formulas = self._load_kpi_formulas()
        self.mock_data_generator = MockDataGenerator()
    
    def _load_kpi_formulas(self) -> Dict[str, Dict]:
        """Load KPI calculation formulas for different verticals"""
        return {
            "marketing_agency": {
                "lead_conversion_rate": {
                    "formula": "converted_leads / total_leads * 100",
                    "description": "Percentage of leads that convert to customers",
                    "unit": "percentage",
                    "target": 15.0
                },
                "cost_per_lead": {
                    "formula": "total_spend / total_leads",
                    "description": "Average cost to acquire a lead",
                    "unit": "currency",
                    "target": 25.0
                },
                "lead_quality_score": {
                    "formula": "sum(lead_scores) / count(leads)",
                    "description": "Average quality score of leads",
                    "unit": "score",
                    "target": 7.5
                },
                "campaign_roi": {
                    "formula": "(revenue - cost) / cost * 100",
                    "description": "Return on investment for campaigns",
                    "unit": "percentage",
                    "target": 300.0
                },
                "monthly_revenue": {
                    "formula": "sum(converted_leads * average_deal_size)",
                    "description": "Total monthly revenue from conversions",
                    "unit": "currency",
                    "target": 50000.0
                }
            },
            "urgent_clinic": {
                "average_wait_time": {
                    "formula": "sum(wait_time_minutes) / count(visits)",
                    "description": "Average time patients wait before being seen",
                    "unit": "minutes",
                    "target": 30.0
                },
                "patient_volume": {
                    "formula": "count(visits) where date(visit_date) = today",
                    "description": "Number of patients seen per day",
                    "unit": "count",
                    "target": 50.0
                },
                "revenue_per_visit": {
                    "formula": "sum(total_cost) / count(visits)",
                    "description": "Average revenue generated per visit",
                    "unit": "currency",
                    "target": 150.0
                },
                "provider_utilization": {
                    "formula": "sum(treatment_time) / sum(shift_time) * 100",
                    "description": "Percentage of time providers are seeing patients",
                    "unit": "percentage",
                    "target": 80.0
                },
                "no_show_rate": {
                    "formula": "count(no_shows) / count(scheduled_visits) * 100",
                    "description": "Percentage of scheduled visits that are no-shows",
                    "unit": "percentage",
                    "target": 10.0
                }
            },
            "local_police": {
                "incident_volume": {
                    "formula": "count(incidents) where date(incident_date) = today",
                    "description": "Number of incidents reported per day",
                    "unit": "count",
                    "target": 15.0
                },
                "average_response_time": {
                    "formula": "sum(response_time_minutes) / count(incidents)",
                    "description": "Average time to respond to incidents",
                    "unit": "minutes",
                    "target": 5.0
                },
                "case_resolution_rate": {
                    "formula": "count(resolved_cases) / count(total_cases) * 100",
                    "description": "Percentage of cases that are resolved",
                    "unit": "percentage",
                    "target": 85.0
                },
                "officer_efficiency": {
                    "formula": "count(incidents_handled) / count(active_officers)",
                    "description": "Average incidents handled per officer per day",
                    "unit": "count",
                    "target": 3.0
                },
                "community_satisfaction": {
                    "formula": "sum(satisfaction_scores) / count(surveys)",
                    "description": "Average community satisfaction score",
                    "unit": "score",
                    "target": 8.0
                }
            }
        }
    
    def calculate_kpi(self, kpi_definition: KPIDefinition, normalized_records: List[NormalizedRecord], 
                     start_date: datetime = None, end_date: datetime = None) -> KPIValue:
        """Calculate KPI value based on normalized records"""
        
        vertical = kpi_definition.vertical
        kpi_name = kpi_definition.name.lower().replace(" ", "_")
        
        # Get formula for this KPI
        formula_config = self.kpi_formulas.get(vertical, {}).get(kpi_name)
        
        if not formula_config:
            # Generate a mock value if no formula exists
            mock_value = self._generate_mock_kpi_value(kpi_name, vertical)
        else:
            # Calculate based on formula (simplified for demo)
            mock_value = self._calculate_formula_value(formula_config, normalized_records, vertical)
        
        # Create KPI value record
        kpi_value = KPIValue(
            tenant_id=kpi_definition.tenant_id,
            kpi_id=kpi_definition.id,
            timestamp=end_date or datetime.utcnow(),
            value=mock_value,
            provenance={
                "source_records": len(normalized_records),
                "calculation_method": "formula_based" if formula_config else "mock_generated",
                "data_quality": "high",
                "formula": formula_config.get("formula") if formula_config else "mock",
                "vertical": vertical
            }
        )
        
        return kpi_value
    
    def _generate_mock_kpi_value(self, kpi_name: str, vertical: str) -> float:
        """Generate realistic mock KPI values"""
        
        # Base values for different KPI types
        base_values = {
            "marketing_agency": {
                "lead_conversion_rate": 12.5,
                "cost_per_lead": 28.50,
                "lead_quality_score": 7.2,
                "campaign_roi": 285.0,
                "monthly_revenue": 45000.0
            },
            "urgent_clinic": {
                "average_wait_time": 35.0,
                "patient_volume": 48.0,
                "revenue_per_visit": 145.0,
                "provider_utilization": 78.0,
                "no_show_rate": 12.0
            },
            "local_police": {
                "incident_volume": 18.0,
                "average_response_time": 6.5,
                "case_resolution_rate": 82.0,
                "officer_efficiency": 2.8,
                "community_satisfaction": 7.9
            }
        }
        
        base_value = base_values.get(vertical, {}).get(kpi_name, 50.0)
        
        # Add some realistic variation
        variation = random.uniform(-0.2, 0.2)  # ±20% variation
        return round(base_value * (1 + variation), 2)
    
    def _calculate_formula_value(self, formula_config: Dict, records: List[NormalizedRecord], vertical: str) -> float:
        """Calculate KPI value using formula (simplified for demo)"""
        
        # For demo purposes, we'll generate realistic values based on the formula type
        formula = formula_config.get("formula", "")
        
        if "conversion" in formula.lower():
            # Lead conversion rate
            base_rate = 12.5
            variation = random.uniform(-0.15, 0.15)
            return round(base_rate * (1 + variation), 2)
        
        elif "cost" in formula.lower():
            # Cost per lead
            base_cost = 28.50
            variation = random.uniform(-0.2, 0.2)
            return round(base_cost * (1 + variation), 2)
        
        elif "wait" in formula.lower():
            # Wait time
            base_time = 35.0
            variation = random.uniform(-0.3, 0.3)
            return round(base_time * (1 + variation), 2)
        
        elif "volume" in formula.lower():
            # Volume metrics
            base_volume = 50.0
            variation = random.uniform(-0.25, 0.25)
            return round(base_volume * (1 + variation), 2)
        
        elif "roi" in formula.lower():
            # ROI
            base_roi = 285.0
            variation = random.uniform(-0.2, 0.2)
            return round(base_roi * (1 + variation), 2)
        
        else:
            # Default calculation
            return self._generate_mock_kpi_value("default", vertical)
    
    def generate_historical_kpi_values(self, kpi_definition: KPIDefinition, days: int = 30) -> List[KPIValue]:
        """Generate historical KPI values for trend analysis"""
        
        values = []
        base_value = self._generate_mock_kpi_value(
            kpi_definition.name.lower().replace(" ", "_"), 
            kpi_definition.vertical
        )
        
        for i in range(days):
            # Create trend with some randomness
            trend_factor = 1 + (i / days) * random.uniform(-0.1, 0.1)
            daily_variation = random.uniform(-0.15, 0.15)
            
            value = base_value * trend_factor * (1 + daily_variation)
            
            kpi_value = KPIValue(
                tenant_id=kpi_definition.tenant_id,
                kpi_id=kpi_definition.id,
                timestamp=datetime.utcnow() - timedelta(days=days-i-1),
                value=round(value, 2),
                provenance={
                    "source_records": random.randint(50, 200),
                    "calculation_method": "historical_generation",
                    "data_quality": "high",
                    "trend_factor": round(trend_factor, 3)
                }
            )
            values.append(kpi_value)
        
        return values

class MockDataGenerator:
    """Generate realistic mock data for different verticals"""
    
    def generate_marketing_data(self, count: int = 100) -> List[Dict]:
        """Generate mock marketing agency data"""
        data = []
        
        for i in range(count):
            lead = {
                "id": f"lead_{i+1:04d}",
                "email": f"lead{i+1}@example.com",
                "full_name": f"Lead {i+1}",
                "company": f"Company {i+1}",
                "source": random.choice(["website", "google_ads", "facebook", "linkedin", "referral"]),
                "status": random.choice(["new", "qualified", "converted"]),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "converted_at": None,
                "value": random.uniform(500, 5000) if random.random() > 0.7 else None,
                "quality_score": random.uniform(5.0, 10.0)
            }
            
            if lead["status"] == "converted":
                lead["converted_at"] = (datetime.utcnow() - timedelta(days=random.randint(0, 15))).isoformat()
            
            data.append(lead)
        
        return data
    
    def generate_clinic_data(self, count: int = 100) -> List[Dict]:
        """Generate mock urgent care clinic data"""
        data = []
        
        for i in range(count):
            visit = {
                "id": f"visit_{i+1:04d}",
                "patient_id": f"patient_{random.randint(1, 50):04d}",
                "first_name": f"Patient{i+1}",
                "last_name": "Smith",
                "check_in_time": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "wait_time_minutes": random.randint(10, 90),
                "treatment_time_minutes": random.randint(15, 60),
                "chief_complaint": random.choice(["Chest pain", "Fever", "Injury", "Headache", "Stomach pain"]),
                "total_cost": random.uniform(100, 300),
                "insurance_coverage": random.uniform(0.7, 0.95)
            }
            data.append(visit)
        
        return data
    
    def generate_police_data(self, count: int = 100) -> List[Dict]:
        """Generate mock police department data"""
        data = []
        
        incident_types = ["Traffic violation", "Theft", "Assault", "Burglary", "Vandalism", "Domestic dispute"]
        
        for i in range(count):
            incident = {
                "id": f"incident_{i+1:04d}",
                "incident_type": random.choice(incident_types),
                "location": f"{random.randint(100, 999)} Main St",
                "reported_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "response_time_minutes": random.randint(2, 15),
                "officer_id": f"officer_{random.randint(1, 20):03d}",
                "status": random.choice(["open", "investigating", "resolved", "closed"]),
                "severity": random.choice(["low", "medium", "high"])
            }
            data.append(incident)
        
        return data

# Global instance
kpi_engine = MockKPIEngine()

