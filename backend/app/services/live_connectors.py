"""
Live Connector Stubs for HubSpot and Google Ads
Provides mock API responses that match real connector formats
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.connector import Connector, RawIngest

class HubSpotConnector:
    """HubSpot connector stub with realistic mock data"""
    
    def __init__(self):
        self.base_url = "https://api.hubapi.com"
        self.mock_contacts = self._generate_mock_contacts()
        self.mock_deals = self._generate_mock_deals()
        self.mock_companies = self._generate_mock_companies()
    
    def _generate_mock_contacts(self) -> List[Dict]:
        """Generate mock HubSpot contacts"""
        contacts = []
        
        first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Edward", "Fiona", "George", "Helen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        companies = ["TechCorp", "StartupIO", "Enterprise Inc", "SmallBiz LLC", "Global Solutions", "Local Business", "Innovation Co", "Digital Agency"]
        
        for i in range(50):
            contact = {
                "id": f"contact_{i+1}",
                "properties": {
                    "email": f"contact{i+1}@example.com",
                    "firstname": random.choice(first_names),
                    "lastname": random.choice(last_names),
                    "company": random.choice(companies),
                    "phone": f"+1-555-{random.randint(1000, 9999)}",
                    "lead_status": random.choice(["new", "qualified", "converted", "unqualified"]),
                    "lifecyclestage": random.choice(["subscriber", "lead", "marketingqualifiedlead", "salesqualifiedlead", "opportunity", "customer"]),
                    "createdate": (datetime.utcnow() - timedelta(days=random.randint(0, 90))).isoformat(),
                    "lastmodifieddate": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                    "hs_lead_status": random.choice(["NEW", "OPEN", "IN_PROGRESS", "OPEN_DEAL", "UNQUALIFIED", "ATTEMPTED_TO_CONTACT", "CONNECTED", "BAD_TIMING"]),
                    "hs_lead_score": random.randint(0, 100),
                    "city": random.choice(["New York", "San Francisco", "Chicago", "Boston", "Seattle", "Austin", "Denver", "Miami"]),
                    "state": random.choice(["NY", "CA", "IL", "MA", "WA", "TX", "CO", "FL"]),
                    "country": "United States"
                },
                "createdAt": (datetime.utcnow() - timedelta(days=random.randint(0, 90))).isoformat(),
                "updatedAt": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "archived": False
            }
            contacts.append(contact)
        
        return contacts
    
    def _generate_mock_deals(self) -> List[Dict]:
        """Generate mock HubSpot deals"""
        deals = []
        
        deal_stages = ["appointmentscheduled", "qualifiedtobuy", "presentationscheduled", "decisionmakerboughtin", "contractsent", "closedwon", "closedlost"]
        deal_names = ["Software License", "Consulting Services", "Marketing Campaign", "Implementation", "Support Package", "Custom Development"]
        
        for i in range(30):
            deal = {
                "id": f"deal_{i+1}",
                "properties": {
                    "dealname": f"{random.choice(deal_names)} - {i+1}",
                    "amount": str(random.randint(5000, 100000)),
                    "dealstage": random.choice(deal_stages),
                    "pipeline": "default",
                    "closedate": (datetime.utcnow() + timedelta(days=random.randint(0, 90))).isoformat(),
                    "createdate": (datetime.utcnow() - timedelta(days=random.randint(0, 60))).isoformat(),
                    "hs_deal_stage_probability": random.randint(10, 100),
                    "hs_deal_amount_calculation_preference": "amount_in_home_currency",
                    "hs_forecast_amount": str(random.randint(5000, 100000)),
                    "hs_forecast_probability": random.randint(10, 100),
                    "hs_forecast_category": random.choice(["BEST_CASE", "LIKELY", "WORST_CASE"]),
                    "hs_next_step": random.choice(["Follow up call", "Send proposal", "Schedule demo", "Review contract", "Close deal"]),
                    "hs_deal_amount_calculation_preference": "amount_in_home_currency"
                },
                "createdAt": (datetime.utcnow() - timedelta(days=random.randint(0, 60))).isoformat(),
                "updatedAt": (datetime.utcnow() - timedelta(days=random.randint(0, 15))).isoformat(),
                "archived": False
            }
            deals.append(deal)
        
        return deals
    
    def _generate_mock_companies(self) -> List[Dict]:
        """Generate mock HubSpot companies"""
        companies = []
        
        company_names = ["TechCorp Inc", "StartupIO LLC", "Enterprise Solutions", "SmallBiz Corp", "Global Innovations", "Local Services", "Digital Marketing Co", "Software Solutions"]
        industries = ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail", "Education", "Consulting", "Real Estate"]
        
        for i in range(20):
            company = {
                "id": f"company_{i+1}",
                "properties": {
                    "name": random.choice(company_names),
                    "domain": f"company{i+1}.com",
                    "industry": random.choice(industries),
                    "city": random.choice(["New York", "San Francisco", "Chicago", "Boston", "Seattle"]),
                    "state": random.choice(["NY", "CA", "IL", "MA", "WA"]),
                    "country": "United States",
                    "numberofemployees": str(random.randint(10, 1000)),
                    "annualrevenue": str(random.randint(1000000, 10000000)),
                    "lifecyclestage": random.choice(["subscriber", "lead", "marketingqualifiedlead", "salesqualifiedlead", "opportunity", "customer"]),
                    "createdate": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat(),
                    "lastmodifieddate": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()
                },
                "createdAt": (datetime.utcnow() - timedelta(days=random.randint(0, 180))).isoformat(),
                "updatedAt": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "archived": False
            }
            companies.append(company)
        
        return companies
    
    def sync_contacts(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync contacts from HubSpot"""
        
        # Simulate API call delay
        import time
        time.sleep(0.1)
        
        # Create raw ingest record
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "contacts",
                "data": self.mock_contacts,
                "metadata": {
                    "total": len(self.mock_contacts),
                    "has_more": False,
                    "offset": 0,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest
    
    def sync_deals(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync deals from HubSpot"""
        
        import time
        time.sleep(0.1)
        
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "deals",
                "data": self.mock_deals,
                "metadata": {
                    "total": len(self.mock_deals),
                    "has_more": False,
                    "offset": 0,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest
    
    def sync_companies(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync companies from HubSpot"""
        
        import time
        time.sleep(0.1)
        
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "companies",
                "data": self.mock_companies,
                "metadata": {
                    "total": len(self.mock_companies),
                    "has_more": False,
                    "offset": 0,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest

class GoogleAdsConnector:
    """Google Ads connector stub with realistic mock data"""
    
    def __init__(self):
        self.base_url = "https://googleads.googleapis.com"
        self.mock_campaigns = self._generate_mock_campaigns()
        self.mock_ad_groups = self._generate_mock_ad_groups()
        self.mock_ads = self._generate_mock_ads()
        self.mock_keywords = self._generate_mock_keywords()
    
    def _generate_mock_campaigns(self) -> List[Dict]:
        """Generate mock Google Ads campaigns"""
        campaigns = []
        
        campaign_types = ["SEARCH", "DISPLAY", "VIDEO", "SHOPPING", "APP"]
        statuses = ["ENABLED", "PAUSED", "REMOVED"]
        
        for i in range(15):
            campaign = {
                "resourceName": f"customers/1234567890/campaigns/{i+1}",
                "id": str(i+1),
                "name": f"Campaign {i+1} - {random.choice(['Search', 'Display', 'Video', 'Shopping'])}",
                "status": random.choice(statuses),
                "servingStatus": "SERVING",
                "advertisingChannelType": random.choice(campaign_types),
                "advertisingChannelSubType": "SEARCH_MOBILE_APP",
                "startDate": (datetime.utcnow() - timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d"),
                "endDate": (datetime.utcnow() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
                "budget": {
                    "resourceName": f"customers/1234567890/campaignBudgets/{i+1}",
                    "amountMicros": str(random.randint(10000000, 100000000)),  # $10-$100
                    "period": "DAILY"
                },
                "biddingStrategyType": random.choice(["TARGET_CPA", "TARGET_ROAS", "MAXIMIZE_CONVERSIONS", "MAXIMIZE_CLICKS"]),
                "targetCpa": {
                    "targetCpaMicros": str(random.randint(1000000, 5000000))  # $1-$5
                } if random.random() > 0.5 else None
            }
            campaigns.append(campaign)
        
        return campaigns
    
    def _generate_mock_ad_groups(self) -> List[Dict]:
        """Generate mock Google Ads ad groups"""
        ad_groups = []
        
        for i in range(30):
            ad_group = {
                "resourceName": f"customers/1234567890/adGroups/{i+1}",
                "id": str(i+1),
                "name": f"Ad Group {i+1}",
                "campaign": f"customers/1234567890/campaigns/{(i % 15) + 1}",
                "status": random.choice(["ENABLED", "PAUSED", "REMOVED"]),
                "type": "SEARCH_STANDARD",
                "cpcBidMicros": str(random.randint(1000000, 10000000)),  # $1-$10
                "cpmBidMicros": str(random.randint(1000000, 5000000))  # $1-$5
            }
            ad_groups.append(ad_group)
        
        return ad_groups
    
    def _generate_mock_ads(self) -> List[Dict]:
        """Generate mock Google Ads"""
        ads = []
        
        headlines = ["Best Software Solution", "Get Results Fast", "Professional Services", "Quality Guaranteed", "Expert Solutions"]
        descriptions = ["Transform your business with our innovative approach", "Join thousands of satisfied customers", "Get started today with our easy setup", "Professional support included", "Proven results in your industry"]
        
        for i in range(50):
            ad = {
                "resourceName": f"customers/1234567890/ads/{i+1}",
                "id": str(i+1),
                "adGroup": f"customers/1234567890/adGroups/{(i % 30) + 1}",
                "status": random.choice(["ENABLED", "PAUSED", "REMOVED"]),
                "type": "RESPONSIVE_SEARCH_AD",
                "responsiveSearchAd": {
                    "headlines": [
                        {"text": random.choice(headlines), "pinnedField": "HEADLINE_1"},
                        {"text": f"{random.choice(headlines)} - {i+1}", "pinnedField": "HEADLINE_2"},
                        {"text": f"Special Offer {i+1}", "pinnedField": "HEADLINE_3"}
                    ],
                    "descriptions": [
                        {"text": random.choice(descriptions), "pinnedField": "DESCRIPTION_1"},
                        {"text": f"{random.choice(descriptions)} - Limited Time", "pinnedField": "DESCRIPTION_2"}
                    ],
                    "path1": "Learn More",
                    "path2": "Get Started"
                }
            }
            ads.append(ad)
        
        return ads
    
    def _generate_mock_keywords(self) -> List[Dict]:
        """Generate mock Google Ads keywords"""
        keywords = []
        
        keyword_texts = ["marketing software", "business solutions", "professional services", "digital marketing", "software development", "consulting services", "business automation", "data analytics"]
        
        for i in range(100):
            keyword = {
                "resourceName": f"customers/1234567890/keywords/{i+1}",
                "id": str(i+1),
                "adGroup": f"customers/1234567890/adGroups/{(i % 30) + 1}",
                "text": random.choice(keyword_texts),
                "matchType": random.choice(["EXACT", "PHRASE", "BROAD"]),
                "status": random.choice(["ENABLED", "PAUSED", "REMOVED"]),
                "cpcBidMicros": str(random.randint(500000, 5000000)),  # $0.50-$5.00
                "qualityInfo": {
                    "qualityScore": random.randint(1, 10),
                    "creativeQualityScore": random.choice(["ABOVE_AVERAGE", "AVERAGE", "BELOW_AVERAGE"]),
                    "postClickQualityScore": random.choice(["ABOVE_AVERAGE", "AVERAGE", "BELOW_AVERAGE"]),
                    "searchPredictedCtr": random.choice(["ABOVE_AVERAGE", "AVERAGE", "BELOW_AVERAGE"])
                }
            }
            keywords.append(keyword)
        
        return keywords
    
    def sync_campaigns(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync campaigns from Google Ads"""
        
        import time
        time.sleep(0.1)
        
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "campaigns",
                "data": self.mock_campaigns,
                "metadata": {
                    "total": len(self.mock_campaigns),
                    "has_more": False,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest
    
    def sync_ad_groups(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync ad groups from Google Ads"""
        
        import time
        time.sleep(0.1)
        
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "adGroups",
                "data": self.mock_ad_groups,
                "metadata": {
                    "total": len(self.mock_ad_groups),
                    "has_more": False,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest
    
    def sync_ads(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync ads from Google Ads"""
        
        import time
        time.sleep(0.1)
        
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "ads",
                "data": self.mock_ads,
                "metadata": {
                    "total": len(self.mock_ads),
                    "has_more": False,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest
    
    def sync_keywords(self, connector: Connector, tenant_id: int) -> RawIngest:
        """Sync keywords from Google Ads"""
        
        import time
        time.sleep(0.1)
        
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "endpoint": "keywords",
                "data": self.mock_keywords,
                "metadata": {
                    "total": len(self.mock_keywords),
                    "has_more": False,
                    "sync_timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest

class LiveConnectorService:
    """Service for managing live connectors"""
    
    def __init__(self):
        self.hubspot = HubSpotConnector()
        self.google_ads = GoogleAdsConnector()
    
    def sync_connector(self, connector: Connector, tenant_id: int) -> List[RawIngest]:
        """Sync data from live connector"""
        
        raw_ingests = []
        
        if connector.type == "hubspot":
            # Sync all HubSpot data
            raw_ingests.append(self.hubspot.sync_contacts(connector, tenant_id))
            raw_ingests.append(self.hubspot.sync_deals(connector, tenant_id))
            raw_ingests.append(self.hubspot.sync_companies(connector, tenant_id))
        
        elif connector.type == "google_ads":
            # Sync all Google Ads data
            raw_ingests.append(self.google_ads.sync_campaigns(connector, tenant_id))
            raw_ingests.append(self.google_ads.sync_ad_groups(connector, tenant_id))
            raw_ingests.append(self.google_ads.sync_ads(connector, tenant_id))
            raw_ingests.append(self.google_ads.sync_keywords(connector, tenant_id))
        
        return raw_ingests

# Global instance
live_connector_service = LiveConnectorService()

