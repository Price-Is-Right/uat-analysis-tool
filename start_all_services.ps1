# Start All GCS Services
# Starts Context Analyzer microservice and API Gateway

Write-Host "🚀 Starting GCS Services..." -ForegroundColor Green

# Start Context Analyzer on port 8001
Write-Host "`n📊 Starting Context Analyzer Agent (port 8001)..." -ForegroundColor Cyan
$contextAnalyzerPath = "C:\Projects\Hack\agents\context-analyzer"
Start-Process python -ArgumentList "$contextAnalyzerPath\service.py" -NoNewWindow -WorkingDirectory $contextAnalyzerPath

# Wait for Context Analyzer to start
Write-Host "⏳ Waiting for Context Analyzer to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Test Context Analyzer health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET -UseBasicParsing
    Write-Host "✅ Context Analyzer is healthy!" -ForegroundColor Green
} catch {
    Write-Host "❌ Context Analyzer failed to start!" -ForegroundColor Red
    exit 1
}

# Start API Gateway on port 8000
Write-Host "`n🌐 Starting API Gateway (port 8000)..." -ForegroundColor Cyan
$gatewayPath = "C:\Projects\Hack"
Start-Process python -ArgumentList "api_gateway.py" -NoNewWindow -WorkingDirectory $gatewayPath

# Wait for Gateway to start
Write-Host "⏳ Waiting for API Gateway to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Test Gateway health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing
    Write-Host "✅ API Gateway is healthy!" -ForegroundColor Green
} catch {
    Write-Host "❌ API Gateway failed to start!" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 All services started successfully!" -ForegroundColor Green
Write-Host "`n📍 Service URLs:" -ForegroundColor Cyan
Write-Host "   - Context Analyzer: http://localhost:8001" -ForegroundColor White
Write-Host "   - API Gateway: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "`n💡 To test the complete pipeline, use:" -ForegroundColor Yellow
Write-Host '   Invoke-WebRequest -Uri "http://localhost:8000/api/analyze" -Method POST -Body ''{"title":"test","description":"test"}'' -ContentType "application/json"' -ForegroundColor White
