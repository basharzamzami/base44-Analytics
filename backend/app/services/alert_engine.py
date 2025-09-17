"""
Alert Engine with Anomaly Detection
Detects anomalies and triggers alerts based on KPI thresholds and patterns
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.kpi import KPIValue, KPIDefinition
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class MockAlertEngine:
    """Alert engine with anomaly detection for demo purposes"""
    
    def __init__(self):
        self.alert_rules = self._load_alert_rules()
        self.anomaly_detector = MockAnomalyDetector()
    
    def _load_alert_rules(self) -> Dict[str, List[Dict]]:
        """Load alert rules for different verticals"""
        return {
            "marketing_agency": [
                {
                    "name": "Low Conversion Rate Alert",
                    "kpi_name": "lead_conversion_rate",
                    "condition": "value < 10",
                    "severity": "high",
                    "description": "Lead conversion rate dropped below 10%"
                },
                {
                    "name": "High Cost Per Lead Alert",
                    "kpi_name": "cost_per_lead",
                    "condition": "value > 50",
                    "severity": "medium",
                    "description": "Cost per lead exceeded $50"
                },
                {
                    "name": "Revenue Drop Alert",
                    "kpi_name": "monthly_revenue",
                    "condition": "value < 30000",
                    "severity": "high",
                    "description": "Monthly revenue dropped below $30,000"
                },
                {
                    "name": "Lead Quality Decline",
                    "kpi_name": "lead_quality_score",
                    "condition": "value < 6.0",
                    "severity": "medium",
                    "description": "Lead quality score below 6.0"
                }
            ],
            "urgent_clinic": [
                {
                    "name": "Long Wait Time Alert",
                    "kpi_name": "average_wait_time",
                    "condition": "value > 60",
                    "severity": "high",
                    "description": "Average wait time exceeded 60 minutes"
                },
                {
                    "name": "Low Patient Volume Alert",
                    "kpi_name": "patient_volume",
                    "condition": "value < 30",
                    "severity": "medium",
                    "description": "Daily patient volume below 30"
                },
                {
                    "name": "High No-Show Rate Alert",
                    "kpi_name": "no_show_rate",
                    "condition": "value > 20",
                    "severity": "medium",
                    "description": "No-show rate exceeded 20%"
                },
                {
                    "name": "Low Provider Utilization",
                    "kpi_name": "provider_utilization",
                    "condition": "value < 60",
                    "severity": "low",
                    "description": "Provider utilization below 60%"
                }
            ],
            "local_police": [
                {
                    "name": "High Incident Volume Alert",
                    "kpi_name": "incident_volume",
                    "condition": "value > 25",
                    "severity": "high",
                    "description": "Daily incident volume exceeded 25"
                },
                {
                    "name": "Slow Response Time Alert",
                    "kpi_name": "average_response_time",
                    "condition": "value > 10",
                    "severity": "high",
                    "description": "Average response time exceeded 10 minutes"
                },
                {
                    "name": "Low Resolution Rate Alert",
                    "kpi_name": "case_resolution_rate",
                    "condition": "value < 70",
                    "severity": "medium",
                    "description": "Case resolution rate below 70%"
                },
                {
                    "name": "Low Community Satisfaction",
                    "kpi_name": "community_satisfaction",
                    "condition": "value < 6.0",
                    "severity": "medium",
                    "description": "Community satisfaction below 6.0"
                }
            ]
        }
    
    def check_kpi_alerts(self, kpi_value: KPIValue, kpi_definition: KPIDefinition) -> List[Alert]:
        """Check if KPI value triggers any alerts"""
        alerts = []
        vertical = kpi_definition.vertical
        rules = self.alert_rules.get(vertical, [])
        
        for rule in rules:
            if rule["kpi_name"] == kpi_definition.name.lower().replace(" ", "_"):
                if self._evaluate_condition(kpi_value.value, rule["condition"]):
                    alert = Alert(
                        tenant_id=kpi_value.tenant_id,
                        kpi_id=kpi_definition.id,
                        rule_json=rule,
                        severity=rule["severity"],
                        details={
                            "triggered_value": kpi_value.value,
                            "threshold": rule["condition"],
                            "kpi_name": kpi_definition.name,
                            "timestamp": kpi_value.timestamp.isoformat()
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    def detect_anomalies(self, kpi_values: List[KPIValue], kpi_definition: KPIDefinition) -> List[Dict]:
        """Detect anomalies in KPI time series"""
        if len(kpi_values) < 10:  # Need minimum data points
            return []
        
        # Extract values and timestamps
        values = [kv.value for kv in kpi_values]
        timestamps = [kv.timestamp for kv in kpi_values]
        
        # Use mock anomaly detector
        anomalies = self.anomaly_detector.detect_anomalies(values, timestamps)
        
        # Convert to alert format
        anomaly_alerts = []
        for anomaly in anomalies:
            alert = Alert(
                tenant_id=kpi_definition.tenant_id,
                kpi_id=kpi_definition.id,
                rule_json={
                    "name": "Anomaly Detected",
                    "type": "anomaly",
                    "severity": "medium",
                    "description": f"Anomaly detected in {kpi_definition.name}"
                },
                severity="medium",
                details={
                    "anomaly_type": anomaly["type"],
                    "anomaly_score": anomaly["score"],
                    "detected_value": anomaly["value"],
                    "expected_range": anomaly["expected_range"],
                    "timestamp": anomaly["timestamp"]
                }
            )
            anomaly_alerts.append(alert)
        
        return anomaly_alerts
    
    def _evaluate_condition(self, value: float, condition: str) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation (for demo)
            if "<" in condition:
                threshold = float(condition.split("<")[1].strip())
                return value < threshold
            elif ">" in condition:
                threshold = float(condition.split(">")[1].strip())
                return value > threshold
            elif "==" in condition:
                threshold = float(condition.split("==")[1].strip())
                return abs(value - threshold) < 0.01
            else:
                return False
        except:
            return False
    
    def generate_mock_alerts(self, tenant_id: int, vertical: str) -> List[Alert]:
        """Generate mock alerts for demo purposes"""
        alerts = []
        rules = self.alert_rules.get(vertical, [])
        
        # Randomly trigger some alerts
        for rule in rules:
            if random.random() < 0.3:  # 30% chance of triggering
                alert = Alert(
                    tenant_id=tenant_id,
                    rule_json=rule,
                    severity=rule["severity"],
                    details={
                        "triggered_value": random.uniform(5, 15) if "conversion" in rule["kpi_name"] else random.uniform(20, 80),
                        "threshold": rule["condition"],
                        "kpi_name": rule["kpi_name"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "mock_alert": True
                    }
                )
                alerts.append(alert)
        
        return alerts

class MockAnomalyDetector:
    """Mock anomaly detector using statistical methods"""
    
    def __init__(self):
        self.z_score_threshold = 2.0
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    
    def detect_anomalies(self, values: List[float], timestamps: List[datetime]) -> List[Dict]:
        """Detect anomalies using multiple methods"""
        anomalies = []
        
        if len(values) < 10:
            return anomalies
        
        # Method 1: Z-Score based detection
        z_score_anomalies = self._detect_z_score_anomalies(values, timestamps)
        anomalies.extend(z_score_anomalies)
        
        # Method 2: Isolation Forest
        isolation_anomalies = self._detect_isolation_forest_anomalies(values, timestamps)
        anomalies.extend(isolation_anomalies)
        
        # Method 3: Trend-based anomalies
        trend_anomalies = self._detect_trend_anomalies(values, timestamps)
        anomalies.extend(trend_anomalies)
        
        return anomalies
    
    def _detect_z_score_anomalies(self, values: List[float], timestamps: List[datetime]) -> List[Dict]:
        """Detect anomalies using Z-score method"""
        anomalies = []
        
        if len(values) < 5:
            return anomalies
        
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return anomalies
        
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            z_score = abs((value - mean_val) / std_val)
            
            if z_score > self.z_score_threshold:
                anomalies.append({
                    "type": "z_score_outlier",
                    "score": z_score,
                    "value": value,
                    "expected_range": [mean_val - 2*std_val, mean_val + 2*std_val],
                    "timestamp": timestamp.isoformat(),
                    "method": "z_score"
                })
        
        return anomalies
    
    def _detect_isolation_forest_anomalies(self, values: List[float], timestamps: List[datetime]) -> List[Dict]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []
        
        if len(values) < 10:
            return anomalies
        
        # Prepare data for isolation forest
        X = np.array(values).reshape(-1, 1)
        
        # Fit isolation forest
        self.isolation_forest.fit(X)
        
        # Predict anomalies
        anomaly_scores = self.isolation_forest.decision_function(X)
        anomaly_predictions = self.isolation_forest.predict(X)
        
        for i, (value, timestamp, score, prediction) in enumerate(zip(values, timestamps, anomaly_scores, anomaly_predictions)):
            if prediction == -1:  # Anomaly detected
                anomalies.append({
                    "type": "isolation_forest_outlier",
                    "score": abs(score),
                    "value": value,
                    "expected_range": [np.percentile(values, 25), np.percentile(values, 75)],
                    "timestamp": timestamp.isoformat(),
                    "method": "isolation_forest"
                })
        
        return anomalies
    
    def _detect_trend_anomalies(self, values: List[float], timestamps: List[datetime]) -> List[Dict]:
        """Detect trend-based anomalies"""
        anomalies = []
        
        if len(values) < 7:
            return anomalies
        
        # Calculate rolling mean and standard deviation
        window_size = min(7, len(values) // 2)
        rolling_mean = []
        rolling_std = []
        
        for i in range(len(values)):
            start_idx = max(0, i - window_size + 1)
            window_values = values[start_idx:i+1]
            rolling_mean.append(np.mean(window_values))
            rolling_std.append(np.std(window_values))
        
        # Detect sudden changes
        for i in range(1, len(values)):
            if rolling_std[i] > 0:
                z_score = abs((values[i] - rolling_mean[i-1]) / rolling_std[i-1])
                
                if z_score > 2.5:  # Higher threshold for trend detection
                    anomalies.append({
                        "type": "trend_anomaly",
                        "score": z_score,
                        "value": values[i],
                        "expected_range": [rolling_mean[i-1] - 2*rolling_std[i-1], rolling_mean[i-1] + 2*rolling_std[i-1]],
                        "timestamp": timestamps[i].isoformat(),
                        "method": "trend_analysis"
                    })
        
        return anomalies
    
    def inject_synthetic_anomalies(self, values: List[float], timestamps: List[datetime], 
                                 anomaly_count: int = 3) -> Tuple[List[float], List[Dict]]:
        """Inject synthetic anomalies for testing"""
        if len(values) < 10:
            return values, []
        
        modified_values = values.copy()
        injected_anomalies = []
        
        # Select random positions for anomalies
        anomaly_positions = random.sample(range(1, len(values)-1), min(anomaly_count, len(values)-2))
        
        for pos in anomaly_positions:
            original_value = modified_values[pos]
            
            # Create different types of anomalies
            anomaly_type = random.choice(["spike", "drop", "outlier"])
            
            if anomaly_type == "spike":
                # Create a spike (2-5x normal value)
                multiplier = random.uniform(2.0, 5.0)
                modified_values[pos] = original_value * multiplier
            elif anomaly_type == "drop":
                # Create a drop (0.1-0.5x normal value)
                multiplier = random.uniform(0.1, 0.5)
                modified_values[pos] = original_value * multiplier
            else:  # outlier
                # Create an extreme outlier
                mean_val = np.mean(values)
                std_val = np.std(values)
                modified_values[pos] = mean_val + random.choice([-1, 1]) * 4 * std_val
            
            injected_anomalies.append({
                "type": f"synthetic_{anomaly_type}",
                "score": 1.0,
                "value": modified_values[pos],
                "original_value": original_value,
                "timestamp": timestamps[pos].isoformat(),
                "method": "synthetic_injection"
            })
        
        return modified_values, injected_anomalies

# Global instance
alert_engine = MockAlertEngine()

