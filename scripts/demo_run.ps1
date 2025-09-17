# Base44 Demo Script - PowerShell Version
# This script demonstrates the end-to-end flow of Base44

Write-Host "🚀 Starting Base44 Demo..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# API base URL
$API_URL = "http://localhost:8000"

# Function to print colored output
function Write-Status {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if API is running
function Test-API {
    Write-Status "Checking if API is running..."
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/health" -Method GET
        Write-Status "API is running ✅"
        return $true
    }
    catch {
        Write-Error "API is not running. Please start with: docker-compose up -d"
        return $false
    }
}

# Register first tenant (Marketing Agency)
function Register-Tenant1 {
    Write-Status "Registering Marketing Agency tenant..."
    
    $body = @{
        tenant = @{
            name = "Acme Marketing Agency"
            plan = "professional"
        }
        user = @{
            email = "admin@acmemarketing.com"
            password = "securepass123"
            role = "owner"
        }
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/register" -Method POST -ContentType "application/json" -Body $body
        $script:tenant1_token = $response.access_token
        $script:tenant1_id = $response.tenant_id
        Write-Status "Marketing Agency registered successfully ✅"
        Write-Status "Tenant ID: $($script:tenant1_id)"
        return $true
    }
    catch {
        Write-Error "Failed to register Marketing Agency: $($_.Exception.Message)"
        return $false
    }
}

# Register second tenant (Urgent Care Clinic)
function Register-Tenant2 {
    Write-Status "Registering Urgent Care Clinic tenant..."
    
    $body = @{
        tenant = @{
            name = "QuickCare Urgent Clinic"
            plan = "starter"
        }
        user = @{
            email = "admin@quickcare.com"
            password = "securepass123"
            role = "owner"
        }
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/register" -Method POST -ContentType "application/json" -Body $body
        $script:tenant2_token = $response.access_token
        $script:tenant2_id = $response.tenant_id
        Write-Status "Urgent Care Clinic registered successfully ✅"
        Write-Status "Tenant ID: $($script:tenant2_id)"
        return $true
    }
    catch {
        Write-Error "Failed to register Urgent Care Clinic: $($_.Exception.Message)"
        return $false
    }
}

# Test tenant isolation
function Test-TenantIsolation {
    Write-Status "Testing tenant isolation..."
    
    $headers = @{
        "Authorization" = "Bearer $script:tenant1_token"
        "X-Tenant-ID" = $script:tenant2_id
    }
    
    try {
        $response = Invoke-WebRequest -Uri "$API_URL/api/v1/connectors/" -Method GET -Headers $headers
        if ($response.StatusCode -eq 403) {
            Write-Status "Tenant isolation working correctly ✅"
            return $true
        } else {
            Write-Error "Tenant isolation test failed - expected 403, got $($response.StatusCode)"
            return $false
        }
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 403) {
            Write-Status "Tenant isolation working correctly ✅"
            return $true
        } else {
            Write-Error "Tenant isolation test failed: $($_.Exception.Message)"
            return $false
        }
    }
}

# Test AI assistant
function Test-AIAssistant {
    Write-Status "Testing AI assistant..."
    
    $headers = @{
        "Authorization" = "Bearer $script:tenant1_token"
        "X-Tenant-ID" = $script:tenant1_id
        "Content-Type" = "application/json"
    }
    
    $body = @{
        question = "What are my current KPIs and how are they performing?"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api/v1/ask" -Method POST -Headers $headers -Body $body
        if ($response.answer -and $response.answer.Length -gt 0) {
            Write-Status "AI assistant working correctly ✅"
            Write-Status "Sample response: $($response.answer.Substring(0, [Math]::Min(100, $response.answer.Length)))..."
            return $true
        } else {
            Write-Warning "AI assistant returned empty response"
            return $false
        }
    }
    catch {
        Write-Warning "AI assistant test failed: $($_.Exception.Message)"
        return $false
    }
}

# Test dashboard
function Test-Dashboard {
    Write-Status "Testing dashboard..."
    
    $headers = @{
        "Authorization" = "Bearer $script:tenant1_token"
        "X-Tenant-ID" = $script:tenant1_id
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/api/v1/dashboard/$($script:tenant1_id)" -Method GET -Headers $headers
        if ($response.tiles -and $response.tiles.Count -gt 0) {
            Write-Status "Dashboard working correctly ✅"
            Write-Status "Dashboard has $($response.tiles.Count) tiles"
            return $true
        } else {
            Write-Warning "Dashboard returned no tiles"
            return $false
        }
    }
    catch {
        Write-Warning "Dashboard test failed: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
function Main {
    Write-Status "Starting Base44 Demo Script"
    Write-Status "================================"
    
    # Check if API is running
    if (-not (Test-API)) {
        Write-Error "Please start Docker Desktop and run: docker-compose up -d"
        return
    }
    
    # Register tenants
    if (-not (Register-Tenant1)) {
        Write-Error "Failed to register first tenant"
        return
    }
    
    if (-not (Register-Tenant2)) {
        Write-Error "Failed to register second tenant"
        return
    }
    
    # Test features
    Test-TenantIsolation
    Test-AIAssistant
    Test-Dashboard
    
    Write-Status "================================"
    Write-Status "Demo completed successfully! 🎉"
    Write-Status ""
    Write-Status "You can now:"
    Write-Status "1. Visit http://localhost:3000 for the frontend"
    Write-Status "2. Visit http://localhost:8000/docs for API documentation"
    Write-Status "3. Use the following credentials to login:"
    Write-Status "   - Marketing Agency: admin@acmemarketing.com / securepass123"
    Write-Status "   - Urgent Care: admin@quickcare.com / securepass123"
    Write-Status ""
    Write-Status "Features demonstrated:"
    Write-Status "✅ Multi-tenant authentication"
    Write-Status "✅ Tenant isolation"
    Write-Status "✅ AI-powered assistant"
    Write-Status "✅ Real-time dashboard"
}

# Run main function
Main

