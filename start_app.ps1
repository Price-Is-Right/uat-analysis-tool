# Startup script for Flask app with Azure OpenAI integration
# Last updated: January 9, 2026
# Azure OpenAI East endpoint

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Issue Tracker System - Startup Script" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Set Azure OpenAI environment variables (East endpoint)
Write-Host "`n[1/4] Setting Azure OpenAI environment variables..." -ForegroundColor Yellow
$env:AZURE_OPENAI_ENDPOINT = 'https://bp-azure-openai-east.openai.azure.com'
$env:AZURE_OPENAI_API_KEY = 'YOUR_AZURE_OPENAI_KEY_HERE'
$env:AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT = 'gpt-4o-02'
$env:AZURE_OPENAI_EMBEDDING_DEPLOYMENT = 'text-embedding-3-large'

Write-Host "   Endpoint: $env:AZURE_OPENAI_ENDPOINT" -ForegroundColor Gray
Write-Host "   Classification Model: $env:AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT" -ForegroundColor Gray
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
