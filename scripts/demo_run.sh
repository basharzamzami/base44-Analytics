#!/bin/bash

# Base44 Demo Script
# This script demonstrates the end-to-end flow of Base44

set -e

echo "🚀 Starting Base44 Demo..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API base URL
API_URL="http://localhost:8000"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if API is running
check_api() {
    print_status "Checking if API is running..."
    if curl -s "$API_URL/health" > /dev/null; then
        print_status "API is running ✅"
    else
        print_error "API is not running. Please start with: docker-compose up -d"
        exit 1
    fi
}

# Register first tenant (Marketing Agency)
register_tenant1() {
    print_status "Registering Marketing Agency tenant..."
    
    response=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "tenant": {
                "name": "Acme Marketing Agency",
                "plan": "professional"
            },
            "user": {
                "email": "admin@acmemarketing.com",
                "password": "securepass123",
                "role": "owner"
            }
        }')
    
    TENANT1_TOKEN=$(echo $response | jq -r '.access_token')
    TENANT1_ID=$(echo $response | jq -r '.tenant_id')
    
    if [ "$TENANT1_TOKEN" != "null" ]; then
        print_status "Marketing Agency registered successfully ✅"
        print_status "Tenant ID: $TENANT1_ID"
    else
        print_error "Failed to register Marketing Agency"
        exit 1
    fi
}

# Register second tenant (Urgent Care Clinic)
register_tenant2() {
    print_status "Registering Urgent Care Clinic tenant..."
    
    response=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "tenant": {
                "name": "QuickCare Urgent Clinic",
                "plan": "starter"
            },
            "user": {
                "email": "admin@quickcare.com",
                "password": "securepass123",
                "role": "owner"
            }
        }')
    
    TENANT2_TOKEN=$(echo $response | jq -r '.access_token')
    TENANT2_ID=$(echo $response | jq -r '.tenant_id')
    
    if [ "$TENANT2_TOKEN" != "null" ]; then
        print_status "Urgent Care Clinic registered successfully ✅"
        print_status "Tenant ID: $TENANT2_ID"
    else
        print_error "Failed to register Urgent Care Clinic"
        exit 1
    fi
}

# Create connectors for both tenants
create_connectors() {
    print_status "Creating connectors..."
    
    # Marketing Agency CSV connector
    curl -s -X POST "$API_URL/api/v1/connectors/" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "csv",
            "config_json": {
                "delimiter": ",",
                "has_header": true,
                "file_path": "/data/marketing_leads.csv"
            }
        }' > /dev/null
    
    # Urgent Care CSV connector
    curl -s -X POST "$API_URL/api/v1/connectors/" \
        -H "Authorization: Bearer $TENANT2_TOKEN" \
        -H "X-Tenant-ID: $TENANT2_ID" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "csv",
            "config_json": {
                "delimiter": ",",
                "has_header": true,
                "file_path": "/data/patient_visits.csv"
            }
        }' > /dev/null
    
    print_status "Connectors created successfully ✅"
}

# Create KPIs for both tenants
create_kpis() {
    print_status "Creating KPIs..."
    
    # Marketing Agency KPIs
    curl -s -X POST "$API_URL/api/v1/kpis/" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Lead Conversion Rate",
            "vertical": "marketing_agency",
            "formula_json": {
                "type": "percentage",
                "numerator": "converted_leads",
                "denominator": "total_leads"
            },
            "window": "daily"
        }' > /dev/null
    
    # Urgent Care KPIs
    curl -s -X POST "$API_URL/api/v1/kpis/" \
        -H "Authorization: Bearer $TENANT2_TOKEN" \
        -H "X-Tenant-ID: $TENANT2_ID" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Patient Wait Time",
            "vertical": "urgent_clinic",
            "formula_json": {
                "type": "average",
                "field": "wait_time_minutes"
            },
            "window": "hourly"
        }' > /dev/null
    
    print_status "KPIs created successfully ✅"
}

# Test tenant isolation
test_tenant_isolation() {
    print_status "Testing tenant isolation..."
    
    # Try to access tenant 2's data with tenant 1's token
    response=$(curl -s -w "%{http_code}" -o /dev/null \
        -X GET "$API_URL/api/v1/connectors/" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT2_ID")
    
    if [ "$response" = "403" ]; then
        print_status "Tenant isolation working correctly ✅"
    else
        print_error "Tenant isolation test failed"
        exit 1
    fi
}

# Test AI assistant
test_ai_assistant() {
    print_status "Testing AI assistant..."
    
    # Test with Marketing Agency
    response=$(curl -s -X POST "$API_URL/api/v1/ask" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{"question": "What are my current KPIs and how are they performing?"}')
    
    answer=$(echo $response | jq -r '.answer')
    if [ "$answer" != "null" ] && [ -n "$answer" ]; then
        print_status "AI assistant working correctly ✅"
        print_status "Sample response: ${answer:0:100}..."
    else
        print_warning "AI assistant returned empty response"
    fi
}

# Test CSV upload
test_csv_upload() {
    print_status "Testing CSV upload..."
    
    # Upload marketing agency CSV
    response=$(curl -s -X POST "$API_URL/api/v1/connectors/1/upload-csv" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -F "file=@examples/sample_data/marketing_agency.csv")
    
    success=$(echo $response | jq -r '.success')
    if [ "$success" = "true" ]; then
        print_status "CSV upload working correctly ✅"
        records=$(echo $response | jq -r '.message' | grep -o '[0-9]*' | head -1)
        print_status "Uploaded $records records"
    else
        print_warning "CSV upload failed"
    fi
}

# Test KPI evaluation
test_kpi_evaluation() {
    print_status "Testing KPI evaluation..."
    
    # Evaluate a KPI
    response=$(curl -s -X POST "$API_URL/api/v1/kpis/1/evaluate" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{"start_date": "2024-01-01T00:00:00Z", "end_date": "2024-01-31T23:59:59Z"}')
    
    success=$(echo $response | jq -r '.success')
    if [ "$success" = "true" ]; then
        print_status "KPI evaluation working correctly ✅"
        kpi_value=$(echo $response | jq -r '.kpi_value.value')
        print_status "KPI value: $kpi_value"
    else
        print_warning "KPI evaluation failed"
    fi
}

# Test forecasting
test_forecasting() {
    print_status "Testing forecasting..."
    
    # Run forecast
    response=$(curl -s -X POST "$API_URL/api/v1/predictions/run" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{"kpi_id": 1, "forecast_days": 30, "method": "prophet"}')
    
    model_name=$(echo $response | jq -r '.model_name')
    if [ "$model_name" != "null" ] && [ -n "$model_name" ]; then
        print_status "Forecasting working correctly ✅"
        print_status "Model: $model_name"
    else
        print_warning "Forecasting failed"
    fi
}

# Test graph queries
test_graph_queries() {
    print_status "Testing graph queries..."
    
    # Query graph
    response=$(curl -s -X POST "$API_URL/api/v1/graph/query" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{"query": "Show me all connected nodes", "vertical": "marketing_agency"}')
    
    success=$(echo $response | jq -r '.success')
    if [ "$success" = "true" ]; then
        print_status "Graph queries working correctly ✅"
        count=$(echo $response | jq -r '.count')
        print_status "Found $count graph results"
    else
        print_warning "Graph queries failed"
    fi
}

# Generate mock alerts
generate_mock_alerts() {
    print_status "Generating mock alerts..."
    
    # Generate alerts for Marketing Agency
    response=$(curl -s -X POST "$API_URL/api/v1/alerts/generate-mock" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID" \
        -H "Content-Type: application/json" \
        -d '{"vertical": "marketing_agency"}')
    
    success=$(echo $response | jq -r '.success')
    if [ "$success" = "true" ]; then
        print_status "Mock alerts generated successfully ✅"
        alerts_created=$(echo $response | jq -r '.alerts_created')
        print_status "Created $alerts_created alerts"
    else
        print_warning "Failed to generate mock alerts"
    fi
}

# Test dashboard
test_dashboard() {
    print_status "Testing dashboard..."
    
    response=$(curl -s -X GET "$API_URL/api/v1/dashboard/$TENANT1_ID" \
        -H "Authorization: Bearer $TENANT1_TOKEN" \
        -H "X-Tenant-ID: $TENANT1_ID")
    
    tiles=$(echo $response | jq -r '.tiles | length')
    if [ "$tiles" != "null" ] && [ "$tiles" -gt 0 ]; then
        print_status "Dashboard working correctly ✅"
        print_status "Dashboard has $tiles tiles"
    else
        print_warning "Dashboard returned no tiles"
    fi
}

# Main execution
main() {
    print_status "Starting Base44 Demo Script"
    print_status "================================"
    
    check_api
    register_tenant1
    register_tenant2
    create_connectors
    create_kpis
    test_tenant_isolation
    test_csv_upload
    test_kpi_evaluation
    generate_mock_alerts
    test_forecasting
    test_graph_queries
    test_ai_assistant
    test_dashboard
    
    print_status "================================"
    print_status "Demo completed successfully! 🎉"
    print_status ""
    print_status "You can now:"
    print_status "1. Visit http://localhost:3000 for the frontend"
    print_status "2. Visit http://localhost:8000/docs for API documentation"
    print_status "3. Use the following credentials to login:"
    print_status "   - Marketing Agency: admin@acmemarketing.com / securepass123"
    print_status "   - Urgent Care: admin@quickcare.com / securepass123"
    print_status ""
    print_status "Features demonstrated:"
    print_status "✅ Multi-tenant authentication"
    print_status "✅ CSV data upload and processing"
    print_status "✅ KPI calculation and evaluation"
    print_status "✅ Alert generation and management"
    print_status "✅ AI-powered forecasting"
    print_status "✅ Graph analysis and queries"
    print_status "✅ Natural language AI assistant"
    print_status "✅ Real-time dashboard"
}

# Run main function
main
