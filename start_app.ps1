# Startup script for Flask app with Azure OpenAI integration
# Last updated: January 2, 2026
# Azure OpenAI North Central endpoint

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Issue Tracker System - Startup Script" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Set Azure OpenAI environment variables (North Central endpoint)
Write-Host "`n[1/4] Setting Azure OpenAI environment variables..." -ForegroundColor Yellow
$env:AZURE_OPENAI_ENDPOINT = 'https://openai-bp-northcentral.openai.azure.com'
$env:AZURE_OPENAI_API_KEY = 'DVVMshKMSgEtLfq3AKLqo12lJ1EshK1UmmGUufi4f8JbGnKCtV1jJQQJ99BFACHrzpqXJ3w3AAABACOGuNep'
$env:AZURE_OPENAI_DEPLOYMENT_NAME = 'gpt-4o-standard'
$env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT = 'text-embedding-3-large'

Write-Host "   Endpoint: $env:AZURE_OPENAI_ENDPOINT" -ForegroundColor Gray
Write-Host "   Classification Model: $env:AZURE_OPENAI_DEPLOYMENT_NAME" -ForegroundColor Gray
Write-Host "   Embedding Model: $env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT" -ForegroundColor Gray

# Stop any existing Python processes
Write-Host "`n[2/4] Stopping any existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Verify Python is available
Write-Host "`n[3/4] Verifying Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "   ERROR: Python not found! Please install Python 3.10 or higher." -ForegroundColor Red
    Write-Host "`n`nPress any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Start Flask application
Write-Host "`n[4/4] Starting Flask application..." -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

python app.py

Write-Host "`n`nApplication stopped." -ForegroundColor Red
Write-Host "Press any key to exit..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
