# Start All GCS Services
# Starts all 8 microservices: API Gateway + 7 Agent Services

Write-Host "🧹 Cleaning up any existing Python services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✅ Cleanup complete" -ForegroundColor Green

Write-Host "`n🚀 Starting GCS Services..." -ForegroundColor Green
Write-Host "⚠️  IMPORTANT: Ensure VPN is OFF for Azure Key Vault access" -ForegroundColor Yellow

# Start API Gateway FIRST (port 8000) - Central routing layer
Write-Host "`n🌐 Starting API Gateway (8000)..." -ForegroundColor Cyan
$gatewayPath = "C:\Projects\Hack"
Start-Process python -ArgumentList "api_gateway.py" -NoNewWindow -WorkingDirectory $gatewayPath

# Wait for Gateway to start (Key Vault + Route imports take ~15 seconds)
Write-Host "⏳ Waiting for API Gateway to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Test Gateway health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing
    Write-Host "✅ API Gateway is healthy!" -ForegroundColor Green
} catch {
    Write-Host "❌ API Gateway failed to start!" -ForegroundColor Red
    Write-Host "   Try running manually: python api_gateway.py" -ForegroundColor Yellow
    exit 1
}

# Start Context Analyzer Agent (port 8001)
Write-Host "`n📊 Starting Context Analyzer Agent (8001)..." -ForegroundColor Cyan
$contextAnalyzerPath = "C:\Projects\Hack\agents\context-analyzer"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $contextAnalyzerPath

# Wait for Context Analyzer to start
Write-Host "⏳ Waiting for Context Analyzer to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Test Context Analyzer health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET -UseBasicParsing
    Write-Host "✅ Context Analyzer is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Context Analyzer may still be starting..." -ForegroundColor Yellow
}

# Start Search Service Agent (port 8002)
Write-Host "`n🔍 Starting Search Service Agent (8002)..." -ForegroundColor Cyan
$searchServicePath = "C:\Projects\Hack\agents\search-service"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $searchServicePath

# Wait for Search Service to start
Write-Host "⏳ Waiting for Search Service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test Search Service health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8002/health" -Method GET -UseBasicParsing
    Write-Host "✅ Search Service is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Search Service may still be starting..." -ForegroundColor Yellow
}

# Start Enhanced Matching Agent (port 8003)
Write-Host "`n🎯 Starting Enhanced Matching Agent (8003)..." -ForegroundColor Cyan
$matchingServicePath = "C:\Projects\Hack\agents\enhanced-matching"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $matchingServicePath

# Wait for Enhanced Matching Service to start (takes longer due to AI initialization)
Write-Host "⏳ Waiting for Enhanced Matching Service to initialize (AI components loading)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Test Enhanced Matching Service health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8003/health" -Method GET -UseBasicParsing
    Write-Host "✅ Enhanced Matching Service is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Enhanced Matching Service may still be starting..." -ForegroundColor Yellow
    Write-Host "   This service takes ~15-20 seconds to initialize AI components." -ForegroundColor Gray
}

# Start UAT Management Agent (port 8004)
Write-Host "`n📋 Starting UAT Management Agent (8004)..." -ForegroundColor Cyan
$uatManagementPath = "C:\Projects\Hack\agents\uat-management"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $uatManagementPath

# Wait for UAT Management to start
Write-Host "⏳ Waiting for UAT Management to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Test UAT Management health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8004/health" -Method GET -UseBasicParsing
    Write-Host "✅ UAT Management is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  UAT Management may still be starting..." -ForegroundColor Yellow
}

# Start LLM Classifier Agent (port 8005)
Write-Host "`n🤖 Starting LLM Classifier Agent (8005)..." -ForegroundColor Cyan
$llmClassifierPath = "C:\Projects\Hack\agents\llm-classifier"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $llmClassifierPath

# Wait for LLM Classifier to start
Write-Host "⏳ Waiting for LLM Classifier to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test LLM Classifier health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8005/health" -Method GET -UseBasicParsing
    Write-Host "✅ LLM Classifier is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  LLM Classifier may still be starting..." -ForegroundColor Yellow
}

# Start Embedding Service Agent (port 8006)
Write-Host "`n🔢 Starting Embedding Service Agent (8006)..." -ForegroundColor Cyan
$embeddingServicePath = "C:\Projects\Hack\agents\embedding-service"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $embeddingServicePath

# Wait for Embedding Service to start
Write-Host "⏳ Waiting for Embedding Service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test Embedding Service health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8006/health" -Method GET -UseBasicParsing
    Write-Host "✅ Embedding Service is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Embedding Service may still be starting..." -ForegroundColor Yellow
}

# Start Vector Search Agent (port 8007)
Write-Host "`n🔎 Starting Vector Search Agent (8007)..." -ForegroundColor Cyan
$vectorSearchPath = "C:\Projects\Hack\agents\vector-search"
Start-Process python -ArgumentList "service.py" -NoNewWindow -WorkingDirectory $vectorSearchPath

# Wait for Vector Search to start
Write-Host "⏳ Waiting for Vector Search to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test Vector Search health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8007/health" -Method GET -UseBasicParsing
    Write-Host "✅ Vector Search is healthy!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Vector Search may still be starting..." -ForegroundColor Yellow
}

Write-Host "`n🎉 All services started successfully!" -ForegroundColor Green
Write-Host "`n📍 Service URLs:" -ForegroundColor Cyan
Write-Host "   - API Gateway: http://localhost:8000 (Central Routing)" -ForegroundColor White
Write-Host "   - Context Analyzer: http://localhost:8001" -ForegroundColor White
Write-Host "   - Search Service: http://localhost:8002" -ForegroundColor White
Write-Host "   - Enhanced Matching: http://localhost:8003" -ForegroundColor White
Write-Host "   - UAT Management: http://localhost:8004" -ForegroundColor White
Write-Host "   - LLM Classifier: http://localhost:8005" -ForegroundColor White
Write-Host "   - Embedding Service: http://localhost:8006" -ForegroundColor White
Write-Host "   - Vector Search: http://localhost:8007" -ForegroundColor White
Write-Host "`n💡 Quick Health Check:" -ForegroundColor Yellow
Write-Host '   Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET' -ForegroundColor White
Write-Host '   Invoke-WebRequest -Uri "http://localhost:8000/api/embedding/embed" -Method POST -Body ''{"text":"test embedding"}'' -ContentType "application/json"' -ForegroundColor White
