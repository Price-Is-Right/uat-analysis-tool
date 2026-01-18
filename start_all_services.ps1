# Start All GCS Services
# Starts Context Analyzer, Search Service, and API Gateway

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

# Start Search Service on port 8002
Write-Host "`n🔍 Starting Search Service Agent (port 8002)..." -ForegroundColor Cyan
$searchServicePath = "C:\Projects\Hack\agents\search-service"
Start-Process python -ArgumentList "$searchServicePath\service.py" -NoNewWindow -WorkingDirectory $searchServicePath

# Wait for Search Service to start
Write-Host "⏳ Waiting for Search Service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test Search Service health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8002/health" -Method GET -UseBasicParsing
    Write-Host "✅ Search Service is healthy!" -ForegroundColor Green
} catch {
    Write-Host "❌ Search Service failed to start!" -ForegroundColor Red
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
Write-Host "   - Search Service: http://localhost:8002" -ForegroundColor White
Write-Host "   - API Gateway: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "`n💡 To test services:" -ForegroundColor Yellow
Write-Host '   # Context Analyzer:' -ForegroundColor Gray
Write-Host '   Invoke-WebRequest -Uri "http://localhost:8000/api/analyze" -Method POST -Body ''{"title":"test","description":"test"}'' -ContentType "application/json"' -ForegroundColor White
Write-Host '   # Search Service:' -ForegroundColor Gray
Write-Host '   Invoke-WebRequest -Uri "http://localhost:8000/api/search" -Method POST -Body ''{"title":"test","description":"test","category":"technical_support","intent":"reporting_issue","domain_entities":{}}'' -ContentType "application/json"' -ForegroundColor White
