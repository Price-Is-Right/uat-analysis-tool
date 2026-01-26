# Comprehensive Startup Script for UAT Analysis Tool
# Starts all services including Admin Service

param(
    [switch]$AdminOnly,
    [switch]$MainAppOnly,
    [switch]$MicroservicesOnly,
    [switch]$All
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "UAT Analysis Tool - Multi-Service Launcher" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

if (-not ($AdminOnly -or $MainAppOnly -or $MicroservicesOnly -or $All)) {
    Write-Host "`nPlease specify which services to start:" -ForegroundColor Yellow
    Write-Host "  -All                Start everything (Main App + Microservices + Admin)" -ForegroundColor White
    Write-Host "  -MainAppOnly        Start only the main Flask app (port 5003)" -ForegroundColor White
    Write-Host "  -MicroservicesOnly  Start only microservices (ports 8000-8003)" -ForegroundColor White
    Write-Host "  -AdminOnly          Start only admin service (port 8004)" -ForegroundColor White
    Write-Host "`nExample:" -ForegroundColor Gray
    Write-Host "  .\start_services.ps1 -All" -ForegroundColor Gray
    Write-Host "  .\start_services.ps1 -AdminOnly" -ForegroundColor Gray
    exit
}

$jobs = @()

# Start Microservices
if ($MicroservicesOnly -or $All) {
    Write-Host "`n[Starting Microservices]" -ForegroundColor Green
    Write-Host "  API Gateway (port 8000)" -ForegroundColor Gray
    Write-Host "  Context Analyzer (port 8001)" -ForegroundColor Gray
    Write-Host "  Search Service (port 8002)" -ForegroundColor Gray
    Write-Host "  Enhanced Matching (port 8003)" -ForegroundColor Gray
    
    $jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\start_all_services.ps1" -PassThru
    Start-Sleep -Seconds 3
}

# Start Main Flask App
if ($MainAppOnly -or $All) {
    Write-Host "`n[Starting Main Flask Application]" -ForegroundColor Green
    Write-Host "  Port: 5003" -ForegroundColor Gray
    Write-Host "  URL:  http://localhost:5003" -ForegroundColor Gray
    
    $jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\start_app.ps1" -PassThru
    Start-Sleep -Seconds 3
}

# Start Admin Service
if ($AdminOnly -or $All) {
    Write-Host "`n[Starting Admin Service]" -ForegroundColor Green
    Write-Host "  Port: 8004" -ForegroundColor Gray
    Write-Host "  URL:  http://localhost:8004" -ForegroundColor Gray
    
    $jobs += Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\start_admin_service.ps1" -PassThru
    Start-Sleep -Seconds 3
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Services Started!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan

if ($All -or ($MainAppOnly -and $AdminOnly)) {
    Write-Host "`nMain Application:  http://localhost:5003" -ForegroundColor White
    Write-Host "Admin Panel:       http://localhost:8004" -ForegroundColor White
}
if ($MicroservicesOnly -or $All) {
    Write-Host "API Gateway:       http://localhost:8000" -ForegroundColor White
}
if ($AdminOnly) {
    Write-Host "Admin Panel:       http://localhost:8004" -ForegroundColor White
}
if ($MainAppOnly) {
    Write-Host "Main Application:  http://localhost:5003" -ForegroundColor White
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C in each window to stop services" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
