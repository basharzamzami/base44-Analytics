"""
LLM Service with Mock Data
Provides deterministic field mapping and AI assistant responses for demo purposes
"""

import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

class MockLLMService:
    """Mock LLM service that provides deterministic responses for demo purposes"""
    
    def __init__(self):
        self.field_mappings = self._load_field_mappings()
        self.assistant_responses = self._load_assistant_responses()
        self.confidence_threshold = 0.8
    
    def _load_field_mappings(self) -> Dict[str, List[Dict]]:
        """Load predefined field mappings for different connector types"""
        return {
            "csv": {
                "marketing_agency": [
                    {
                        "source_field": "email",
                        "target_field": "email",
                        "confidence": 0.95,
                        "suggested_transformation": "none",
                        "description": "Direct email mapping"
                    },
                    {
                        "source_field": "full_name",
                        "target_field": "full_name",
                        "confidence": 0.92,
                        "suggested_transformation": "none",
                        "description": "Direct name mapping"
                    },
                    {
                        "source_field": "company",
                        "target_field": "company",
                        "confidence": 0.88,
                        "suggested_transformation": "none",
                        "description": "Direct company mapping"
                    },
                    {
                        "source_field": "source",
                        "target_field": "source",
                        "confidence": 0.90,
                        "suggested_transformation": "lowercase",
                        "description": "Convert to lowercase for consistency"
                    },
                    {
                        "source_field": "status",
                        "target_field": "status",
                        "confidence": 0.85,
                        "suggested_transformation": "normalize_status",
                        "description": "Normalize status values"
                    },
                    {
                        "source_field": "created_at",
                        "target_field": "created_at",
                        "confidence": 0.93,
                        "suggested_transformation": "parse_datetime",
                        "description": "Parse datetime string"
                    },
                    {
                        "source_field": "value",
                        "target_field": "value",
                        "confidence": 0.87,
                        "suggested_transformation": "parse_float",
                        "description": "Parse numeric value"
                    }
                ],
                "urgent_clinic": [
                    {
                        "source_field": "first_name",
                        "target_field": "first_name",
                        "confidence": 0.96,
                        "suggested_transformation": "none",
                        "description": "Direct first name mapping"
                    },
                    {
                        "source_field": "last_name",
                        "target_field": "last_name",
                        "confidence": 0.96,
                        "suggested_transformation": "none",
                        "description": "Direct last name mapping"
                    },
                    {
                        "source_field": "date_of_birth",
                        "target_field": "date_of_birth",
                        "confidence": 0.94,
                        "suggested_transformation": "parse_date",
                        "description": "Parse date string"
                    },
                    {
                        "source_field": "phone",
                        "target_field": "phone",
                        "confidence": 0.89,
                        "suggested_transformation": "normalize_phone",
                        "description": "Normalize phone number format"
                    },
                    {
                        "source_field": "email",
                        "target_field": "email",
                        "confidence": 0.91,
                        "suggested_transformation": "lowercase",
                        "description": "Convert email to lowercase"
                    },
                    {
                        "source_field": "insurance_provider",
                        "target_field": "insurance_provider",
                        "confidence": 0.88,
                        "suggested_transformation": "none",
                        "description": "Direct insurance provider mapping"
                    },
                    {
                        "source_field": "insurance_id",
                        "target_field": "insurance_id",
                        "confidence": 0.92,
                        "suggested_transformation": "none",
                        "description": "Direct insurance ID mapping"
                    }
                ],
                "local_police": [
                    {
                        "source_field": "incident_id",
                        "target_field": "incident_id",
                        "confidence": 0.98,
                        "suggested_transformation": "none",
                        "description": "Direct incident ID mapping"
                    },
                    {
                        "source_field": "incident_type",
                        "target_field": "incident_type",
                        "confidence": 0.90,
                        "suggested_transformation": "normalize_category",
                        "description": "Normalize incident category"
                    },
                    {
                        "source_field": "location",
                        "target_field": "location",
                        "confidence": 0.85,
                        "suggested_transformation": "geocode",
                        "description": "Geocode location for mapping"
                    },
                    {
                        "source_field": "reported_at",
                        "target_field": "reported_at",
                        "confidence": 0.94,
                        "suggested_transformation": "parse_datetime",
                        "description": "Parse incident timestamp"
                    },
                    {
                        "source_field": "officer_id",
                        "target_field": "officer_id",
                        "confidence": 0.92,
                        "suggested_transformation": "none",
                        "description": "Direct officer ID mapping"
                    },
                    {
                        "source_field": "status",
                        "target_field": "status",
                        "confidence": 0.88,
                        "suggested_transformation": "normalize_status",
                        "description": "Normalize case status"
                    }
                ]
            },
            "hubspot": {
                "contacts": [
                    {
                        "source_field": "properties.email",
                        "target_field": "email",
                        "confidence": 0.95,
                        "suggested_transformation": "none",
                        "description": "HubSpot contact email"
                    },
                    {
                        "source_field": "properties.firstname",
                        "target_field": "first_name",
                        "confidence": 0.92,
                        "suggested_transformation": "none",
                        "description": "HubSpot first name"
                    },
                    {
                        "source_field": "properties.lastname",
                        "target_field": "last_name",
                        "confidence": 0.92,
                        "suggested_transformation": "none",
                        "description": "HubSpot last name"
                    },
                    {
                        "source_field": "properties.company",
                        "target_field": "company",
                        "confidence": 0.88,
                        "suggested_transformation": "none",
                        "description": "HubSpot company"
                    },
                    {
                        "source_field": "properties.lead_status",
                        "target_field": "status",
                        "confidence": 0.85,
                        "suggested_transformation": "map_lead_status",
                        "description": "Map HubSpot lead status"
                    },
                    {
                        "source_field": "properties.createdate",
                        "target_field": "created_at",
                        "confidence": 0.93,
                        "suggested_transformation": "parse_timestamp",
                        "description": "Parse HubSpot timestamp"
                    }
                ]
            },
            "google_ads": {
                "campaigns": [
                    {
                        "source_field": "campaign.id",
                        "target_field": "campaign_id",
                        "confidence": 0.98,
                        "suggested_transformation": "none",
                        "description": "Google Ads campaign ID"
                    },
                    {
                        "source_field": "campaign.name",
                        "target_field": "campaign_name",
                        "confidence": 0.95,
                        "suggested_transformation": "none",
                        "description": "Google Ads campaign name"
                    },
                    {
                        "source_field": "metrics.clicks",
                        "target_field": "clicks",
                        "confidence": 0.97,
                        "suggested_transformation": "parse_int",
                        "description": "Parse click count"
                    },
                    {
                        "source_field": "metrics.impressions",
                        "target_field": "impressions",
                        "confidence": 0.97,
                        "suggested_transformation": "parse_int",
                        "description": "Parse impression count"
                    },
                    {
                        "source_field": "metrics.cost_micros",
                        "target_field": "cost",
                        "confidence": 0.96,
                        "suggested_transformation": "micros_to_dollars",
                        "description": "Convert micros to dollars"
                    },
                    {
                        "source_field": "segments.date",
                        "target_field": "date",
                        "confidence": 0.94,
                        "suggested_transformation": "parse_date",
                        "description": "Parse campaign date"
                    }
                ]
            }
        }
    
    def _load_assistant_responses(self) -> Dict[str, Dict]:
        """Load predefined assistant responses for different question types"""
        return {
            "kpi_questions": {
                "patterns": ["kpi", "performance", "metrics", "conversion", "revenue"],
                "responses": [
                    {
                        "answer": "Based on your current KPIs, I can see that lead conversion rates have increased by 15% this month compared to last month. Your top-performing campaign is the Google Ads search campaign with a 3.2% conversion rate.",
                        "suggested_actions": [
                            {
                                "action_type": "optimize_campaign",
                                "title": "Optimize Google Ads Campaign",
                                "description": "Increase budget for the top-performing search campaign by 20%",
                                "confidence": 0.85
                            },
                            {
                                "action_type": "create_alert",
                                "title": "Set Up Conversion Alert",
                                "description": "Create an alert to monitor conversion rate drops below 2.5%",
                                "confidence": 0.75
                            }
                        ],
                        "sources": ["kpi_values", "campaign_performance", "conversion_analytics"],
                        "confidence_score": 0.82
                    },
                    {
                        "answer": "Your marketing KPIs show strong performance this quarter. Lead volume is up 25%, cost per lead decreased by 12%, and ROI improved to 320%. The Facebook campaign is your most efficient channel.",
                        "suggested_actions": [
                            {
                                "action_type": "scale_campaign",
                                "title": "Scale Facebook Campaign",
                                "description": "Increase Facebook ad spend by 30% to capitalize on strong performance",
                                "confidence": 0.88
                            }
                        ],
                        "sources": ["kpi_values", "campaign_analytics", "roi_analysis"],
                        "confidence_score": 0.87
                    }
                ]
            },
            "alert_questions": {
                "patterns": ["alert", "issue", "problem", "warning", "critical"],
                "responses": [
                    {
                        "answer": "I found 3 active alerts in your system. The most critical one is a 40% drop in lead quality score, which started 2 days ago. This appears to be related to changes in your landing page traffic sources.",
                        "suggested_actions": [
                            {
                                "action_type": "investigate_issue",
                                "title": "Investigate Lead Quality Drop",
                                "description": "Review traffic sources and landing page performance for the last 7 days",
                                "confidence": 0.90
                            },
                            {
                                "action_type": "create_task",
                                "title": "Fix Landing Page Issues",
                                "description": "Assign task to marketing team to optimize landing page conversion",
                                "confidence": 0.80
                            }
                        ],
                        "sources": ["alerts", "lead_quality_metrics", "traffic_analysis"],
                        "confidence_score": 0.88
                    }
                ]
            },
            "forecast_questions": {
                "patterns": ["forecast", "prediction", "trend", "future", "next month", "next quarter"],
                "responses": [
                    {
                        "answer": "Based on current trends, I predict that your lead volume will increase by 25% over the next 30 days, but conversion rates may drop by 5% due to increased competition. Revenue is projected to grow by 18%.",
                        "suggested_actions": [
                            {
                                "action_type": "prepare_scaling",
                                "title": "Prepare for Lead Volume Increase",
                                "description": "Scale up your sales team capacity to handle 25% more leads",
                                "confidence": 0.78
                            },
                            {
                                "action_type": "optimize_conversion",
                                "title": "Improve Conversion Rates",
                                "description": "Implement A/B testing for landing pages to maintain conversion rates",
                                "confidence": 0.72
                            }
                        ],
                        "sources": ["forecasting_model", "historical_data", "market_trends"],
                        "confidence_score": 0.75
                    }
                ]
            },
            "general_questions": {
                "patterns": ["help", "what", "how", "show", "explain"],
                "responses": [
                    {
                        "answer": "I can help you with KPI analysis, alert management, forecasting, and optimization recommendations. I can analyze your data to provide insights on lead generation, conversion rates, campaign performance, and more.",
                        "suggested_actions": [
                            {
                                "action_type": "explore_dashboard",
                                "title": "View Dashboard",
                                "description": "Check your main dashboard for an overview of key metrics",
                                "confidence": 0.60
                            }
                        ],
                        "sources": ["general_knowledge"],
                        "confidence_score": 0.50
                    }
                ]
            }
        }
    
    def suggest_field_mapping(self, connector_type: str, vertical: str, sample_data: Dict) -> Dict:
        """Suggest field mappings for a connector"""
        mappings = self.field_mappings.get(connector_type, {}).get(vertical, [])
        
        # Add some randomness to confidence scores for realism
        for mapping in mappings:
            mapping["confidence"] = max(0.5, min(0.99, mapping["confidence"] + random.uniform(-0.1, 0.1)))
        
        return {
            "suggested_mappings": mappings,
            "confidence_threshold": self.confidence_threshold,
            "total_fields": len(sample_data) if isinstance(sample_data, dict) else 0,
            "mapped_fields": len(mappings)
        }
    
    def process_ai_query(self, question: str, tenant_id: int, context: Dict = None) -> Dict:
        """Process AI assistant query and return response"""
        question_lower = question.lower()
        
        # Find matching response category
        for category, data in self.assistant_responses.items():
            for pattern in data["patterns"]:
                if pattern in question_lower:
                    response = random.choice(data["responses"])
                    
                    # Add some randomness to confidence
                    response["confidence_score"] = max(0.3, min(0.95, 
                        response["confidence_score"] + random.uniform(-0.1, 0.1)))
                    
                    # Add provenance with mock data
                    response["provenance"] = [
                        {
                            "source": "kpi_engine",
                            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                            "data_points": random.randint(100, 500)
                        },
                        {
                            "source": "alert_system",
                            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 30))).isoformat(),
                            "data_points": random.randint(1, 10)
                        }
                    ]
                    
                    return response
        
        # Default response if no pattern matches
        return {
            "answer": "I can help you with KPI analysis, alert management, forecasting, and optimization recommendations. Could you be more specific about what you'd like to know?",
            "suggested_actions": [
                {
                    "action_type": "explore_dashboard",
                    "title": "View Dashboard",
                    "description": "Check your main dashboard for an overview of key metrics",
                    "confidence": 0.60
                }
            ],
            "sources": ["general_knowledge"],
            "confidence_score": 0.50,
            "provenance": []
        }
    
    def generate_mock_insights(self, vertical: str, data_type: str) -> List[Dict]:
        """Generate mock insights for a specific vertical and data type"""
        insights = []
        
        if vertical == "marketing_agency":
            insights = [
                {
                    "type": "trend",
                    "title": "Lead Volume Increasing",
                    "description": "Lead volume has increased by 25% over the last 30 days",
                    "confidence": 0.85,
                    "impact": "positive"
                },
                {
                    "type": "anomaly",
                    "title": "Conversion Rate Drop",
                    "description": "Conversion rate dropped by 15% in the last week",
                    "confidence": 0.78,
                    "impact": "negative"
                },
                {
                    "type": "recommendation",
                    "title": "Optimize Ad Spend",
                    "description": "Reallocate 20% of budget from display to search ads",
                    "confidence": 0.82,
                    "impact": "neutral"
                }
            ]
        elif vertical == "urgent_clinic":
            insights = [
                {
                    "type": "trend",
                    "title": "Patient Volume Stable",
                    "description": "Patient volume has remained consistent at 45-50 patients per day",
                    "confidence": 0.90,
                    "impact": "neutral"
                },
                {
                    "type": "anomaly",
                    "title": "Wait Time Spike",
                    "description": "Average wait time increased to 65 minutes yesterday",
                    "confidence": 0.88,
                    "impact": "negative"
                },
                {
                    "type": "recommendation",
                    "title": "Staff Optimization",
                    "description": "Consider adding one more provider during peak hours",
                    "confidence": 0.75,
                    "impact": "positive"
                }
            ]
        elif vertical == "local_police":
            insights = [
                {
                    "type": "trend",
                    "title": "Incident Volume Decreasing",
                    "description": "Total incidents decreased by 12% this month",
                    "confidence": 0.87,
                    "impact": "positive"
                },
                {
                    "type": "anomaly",
                    "title": "Response Time Increase",
                    "description": "Average response time increased to 8.5 minutes",
                    "confidence": 0.82,
                    "impact": "negative"
                },
                {
                    "type": "recommendation",
                    "title": "Patrol Optimization",
                    "description": "Increase patrol frequency in downtown area during evening hours",
                    "confidence": 0.79,
                    "impact": "positive"
                }
            ]
        
        return insights

# Global instance
llm_service = MockLLMService()

