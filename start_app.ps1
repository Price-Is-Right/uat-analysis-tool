# Startup script for Flask app with Azure OpenAI integration
# Last updated: January 9, 2026
# Azure OpenAI East endpoint

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Issue Tracker System - Startup Script" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Set Azure OpenAI environment variables (East endpoint)
Write-Host "`n[1/4] Setting Azure OpenAI environment variables..." -ForegroundColor Yellow

# Load from Key Vault via keyvault_config.py
Write-Host "   Loading secrets from Azure Key Vault..." -ForegroundColor Gray
$kvConfig = python -c "from keyvault_config import get_keyvault_config; kv = get_keyvault_config(); print(f'{kv.azure_openai_endpoint}|{kv.azure_openai_api_key}|{kv.azure_openai_classification_deployment}|{kv.azure_openai_embedding_deployment}')"
$parts = $kvConfig -split '\|'
$env:AZURE_OPENAI_ENDPOINT = $parts[0]
$env:AZURE_OPENAI_API_KEY = $parts[1]
$env:AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT = $parts[2]
$env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT = $parts[3]

Write-Host "   Endpoint: $env:AZURE_OPENAI_ENDPOINT" -ForegroundColor Gray
Write-Host "   Classification Model: $env:AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT" -ForegroundColor Gray
Write-Host "   Embedding Model: $env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT" -ForegroundColor Gray

# Check for existing Python processes (but don't stop them aggressively)
Write-Host "`n[2/4] Checking for existing Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "   Found $($pythonProcesses.Count) Python process(es) running" -ForegroundColor Gray
}
Start-Sleep -Seconds 1

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
