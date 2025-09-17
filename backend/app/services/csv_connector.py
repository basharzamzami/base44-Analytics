"""
CSV Connector Service
Handles CSV file upload, parsing, and data extraction
"""

import csv
import io
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.connector import Connector, RawIngest, NormalizedRecord
from app.services.llm_service import llm_service

class CSVConnectorService:
    """Service for handling CSV data ingestion and processing"""
    
    def __init__(self):
        self.supported_delimiters = [',', ';', '\t', '|']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def process_csv_upload(self, file_content: bytes, connector: Connector, 
                          tenant_id: int) -> Dict[str, Any]:
        """Process uploaded CSV file"""
        
        try:
            # Parse CSV content
            csv_data = self._parse_csv_content(file_content, connector.config_json)
            
            # Store raw data
            raw_ingest = self._store_raw_data(csv_data, connector, tenant_id)
            
            # Generate field mapping suggestions
            mapping_suggestions = self._generate_mapping_suggestions(
                csv_data, connector, tenant_id
            )
            
            return {
                "success": True,
                "records_processed": len(csv_data),
                "raw_ingest_id": raw_ingest.id,
                "mapping_suggestions": mapping_suggestions,
                "sample_data": csv_data[:5] if csv_data else []
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "records_processed": 0
            }
    
    def _parse_csv_content(self, file_content: bytes, config: Dict) -> List[Dict]:
        """Parse CSV content into list of dictionaries"""
        
        # Get configuration
        delimiter = config.get('delimiter', ',')
        has_header = config.get('has_header', True)
        encoding = config.get('encoding', 'utf-8')
        
        try:
            # Decode file content
            text_content = file_content.decode(encoding)
            
            # Parse CSV
            csv_reader = csv.DictReader(
                io.StringIO(text_content),
                delimiter=delimiter
            )
            
            data = []
            for row in csv_reader:
                # Clean up the row data
                cleaned_row = {}
                for key, value in row.items():
                    if key:  # Skip empty column names
                        cleaned_key = key.strip()
                        cleaned_value = value.strip() if value else ""
                        cleaned_row[cleaned_key] = cleaned_value
                
                if cleaned_row:  # Only add non-empty rows
                    data.append(cleaned_row)
            
            return data
            
        except Exception as e:
            raise Exception(f"Failed to parse CSV: {str(e)}")
    
    def _store_raw_data(self, csv_data: List[Dict], connector: Connector, 
                       tenant_id: int) -> RawIngest:
        """Store raw CSV data in database"""
        
        # Create raw ingest record
        raw_ingest = RawIngest(
            tenant_id=tenant_id,
            connector_id=connector.id,
            payload_json={
                "data": csv_data,
                "metadata": {
                    "file_type": "csv",
                    "record_count": len(csv_data),
                    "columns": list(csv_data[0].keys()) if csv_data else [],
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return raw_ingest
    
    def _generate_mapping_suggestions(self, csv_data: List[Dict], connector: Connector, 
                                    tenant_id: int) -> Dict:
        """Generate field mapping suggestions using LLM service"""
        
        if not csv_data:
            return {"suggested_mappings": [], "confidence_threshold": 0.8}
        
        # Get sample data for mapping
        sample_data = csv_data[0] if csv_data else {}
        
        # Determine vertical based on connector type or data content
        vertical = self._detect_vertical(sample_data, connector)
        
        # Get mapping suggestions from LLM service
        mapping_suggestions = llm_service.suggest_field_mapping(
            connector_type="csv",
            vertical=vertical,
            sample_data=sample_data
        )
        
        return mapping_suggestions
    
    def _detect_vertical(self, sample_data: Dict, connector: Connector) -> str:
        """Detect vertical based on data content"""
        
        # Check for marketing agency indicators
        marketing_indicators = ['email', 'lead', 'campaign', 'conversion', 'source']
        if any(indicator in str(sample_data).lower() for indicator in marketing_indicators):
            return "marketing_agency"
        
        # Check for clinic indicators
        clinic_indicators = ['patient', 'visit', 'diagnosis', 'insurance', 'provider']
        if any(indicator in str(sample_data).lower() for indicator in clinic_indicators):
            return "urgent_clinic"
        
        # Check for police indicators
        police_indicators = ['incident', 'officer', 'suspect', 'case', 'crime']
        if any(indicator in str(sample_data).lower() for indicator in police_indicators):
            return "local_police"
        
        # Default to marketing agency
        return "marketing_agency"
    
    def normalize_csv_data(self, raw_ingest: RawIngest, mapping_config: Dict, 
                          tenant_id: int) -> List[NormalizedRecord]:
        """Normalize CSV data based on mapping configuration"""
        
        csv_data = raw_ingest.payload_json.get("data", [])
        mappings = mapping_config.get("mappings", {})
        
        normalized_records = []
        
        for i, row in enumerate(csv_data):
            # Apply field mappings
            normalized_data = self._apply_field_mappings(row, mappings)
            
            # Determine entity type
            entity_type = self._determine_entity_type(normalized_data, mappings)
            
            # Create normalized record
            normalized_record = NormalizedRecord(
                tenant_id=tenant_id,
                entity_type=entity_type,
                canonical_json=normalized_data,
                source_refs_json={
                    "raw_ingest_id": raw_ingest.id,
                    "row_index": i,
                    "original_data": row
                }
            )
            
            normalized_records.append(normalized_record)
        
        return normalized_records
    
    def _apply_field_mappings(self, row: Dict, mappings: Dict) -> Dict:
        """Apply field mappings to transform data"""
        
        normalized_data = {}
        
        for source_field, target_field in mappings.items():
            if source_field in row:
                value = row[source_field]
                
                # Apply transformations if specified
                transformed_value = self._apply_transformation(value, target_field)
                normalized_data[target_field] = transformed_value
        
        return normalized_data
    
    def _apply_transformation(self, value: str, target_field: str) -> Any:
        """Apply data transformation based on target field"""
        
        if not value:
            return None
        
        # String transformations
        if target_field in ['email', 'source']:
            return value.lower().strip()
        
        # Date transformations
        if 'date' in target_field or 'time' in target_field:
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00')).isoformat()
            except:
                return value
        
        # Numeric transformations
        if target_field in ['value', 'cost', 'budget', 'amount']:
            try:
                return float(value.replace('$', '').replace(',', ''))
            except:
                return value
        
        # Boolean transformations
        if target_field in ['active', 'enabled', 'converted']:
            return value.lower() in ['true', '1', 'yes', 'active', 'converted']
        
        return value
    
    def _determine_entity_type(self, normalized_data: Dict, mappings: Dict) -> str:
        """Determine entity type based on normalized data"""
        
        # Check for lead indicators
        if any(field in normalized_data for field in ['email', 'lead_id', 'conversion']):
            return "lead"
        
        # Check for campaign indicators
        if any(field in normalized_data for field in ['campaign_id', 'budget', 'platform']):
            return "campaign"
        
        # Check for patient indicators
        if any(field in normalized_data for field in ['patient_id', 'first_name', 'last_name']):
            return "patient"
        
        # Check for visit indicators
        if any(field in normalized_data for field in ['visit_id', 'chief_complaint', 'diagnosis']):
            return "visit"
        
        # Check for incident indicators
        if any(field in normalized_data for field in ['incident_id', 'incident_type', 'location']):
            return "incident"
        
        # Default entity type
        return "record"
    
    def validate_csv_file(self, file_content: bytes, config: Dict) -> Dict[str, Any]:
        """Validate CSV file before processing"""
        
        try:
            # Check file size
            if len(file_content) > self.max_file_size:
                return {
                    "valid": False,
                    "error": f"File too large. Maximum size: {self.max_file_size / 1024 / 1024:.1f}MB"
                }
            
            # Try to parse CSV
            csv_data = self._parse_csv_content(file_content, config)
            
            if not csv_data:
                return {
                    "valid": False,
                    "error": "No data found in CSV file"
                }
            
            # Check for required columns
            required_columns = config.get('required_columns', [])
            if required_columns:
                missing_columns = []
                for col in required_columns:
                    if col not in csv_data[0]:
                        missing_columns.append(col)
                
                if missing_columns:
                    return {
                        "valid": False,
                        "error": f"Missing required columns: {', '.join(missing_columns)}"
                    }
            
            return {
                "valid": True,
                "record_count": len(csv_data),
                "columns": list(csv_data[0].keys()) if csv_data else [],
                "sample_row": csv_data[0] if csv_data else {}
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"CSV validation failed: {str(e)}"
            }

# Global instance
csv_connector = CSVConnectorService()

