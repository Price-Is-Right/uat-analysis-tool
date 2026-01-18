# Start GCS API Gateway
# This script starts the API Gateway in development mode

Write-Host "🚀 Starting GCS API Gateway..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Install/update dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements-gateway.txt --quiet

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  GCS API Gateway - Phase 3" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 API Gateway: http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Docs: http://localhost:8000/api/docs" -ForegroundColor Green
Write-Host "📖 ReDoc: http://localhost:8000/api/redoc" -ForegroundColor Green
Write-Host "💚 Health Check: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start the API Gateway
python api_gateway.py
