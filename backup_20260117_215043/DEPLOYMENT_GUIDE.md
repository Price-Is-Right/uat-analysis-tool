# GCS Microservices Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Service-by-Service Deployment](#service-by-service-deployment)
4. [Configuration](#configuration)
5. [Monitoring & Health Checks](#monitoring--health-checks)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## ✅ Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **pip**: Latest version
- **Git**: For version control
- **PowerShell**: 5.1+ (Windows) or PowerShell Core (cross-platform)

### Azure Services
- **Azure OpenAI**: Required for AI services
  - GPT-4 deployment (gpt-4-32k)
  - text-embedding-3-large deployment
- **Application Insights**: Optional (for monitoring)
- **Azure DevOps**: Optional (for ADO integration)

### Environment Variables
Create a `.env` file or set these environment variables:

```bash
# Azure OpenAI (REQUIRED)
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-32k
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Application Insights (OPTIONAL)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...

# Azure DevOps (OPTIONAL - for Enhanced Matching)
AZURE_DEVOPS_ORG=https://dev.azure.com/your-org
AZURE_DEVOPS_PROJECT=your-project
```

### Python Dependencies
All services require:
```bash
pip install fastapi uvicorn pydantic httpx
```

Service-specific dependencies are in each service's `requirements.txt`.

---

## 🚀 Quick Start

### Option 1: Start All Services (Recommended)
```powershell
cd C:\Projects\Hack
.\start_all_services.ps1
```

This script:
1. Starts all 8 services in sequence
2. Waits for each service to be healthy
3. Displays service URLs
4. Shows test examples

Expected output:
```
🚀 Starting GCS Services...
✅ Context Analyzer is healthy!
✅ Search Service is healthy!
✅ Enhanced Matching Service is healthy!
✅ UAT Management Service is healthy!
✅ LLM Classifier is healthy!
✅ Embedding Service is healthy!
✅ Vector Search is healthy!
✅ API Gateway is healthy!

🎉 All services started successfully!
```

### Option 2: Start Services Individually
```powershell
# Service 1: Context Analyzer
cd C:\Projects\Hack\agents\context-analyzer
python service.py

# Service 2: Search Service
cd C:\Projects\Hack\agents\search-service
python service.py

# ... and so on for each service

# Service 8: API Gateway
cd C:\Projects\Hack
python api_gateway.py
```

### Verify Deployment
```powershell
# Check all services
$services = @(8001, 8002, 8003, 8004, 8005, 8006, 8007, 8000)
foreach ($port in $services) {
    $response = Invoke-WebRequest "http://localhost:$port/health"
    Write-Host "Port $port: $($response.StatusCode)"
}
```

### Test End-to-End
```powershell
python test_end_to_end.py
```

---

## 🎯 Service-by-Service Deployment

### 1. Context Analyzer (Port 8001)

**Location**: `agents/context-analyzer/`

**Start Command**:
```powershell
cd agents\context-analyzer
python service.py
```

**Dependencies**:
- Azure OpenAI (GPT-4)
- `ai_config.py`
- `cache_manager.py`
- `intelligent_context_analyzer.py`

**Configuration**:
```python
# In ai_config.py
AZURE_OPENAI_ENDPOINT = "https://..."
AZURE_OPENAI_KEY = "..."
```

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8001/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "context-analyzer",
  "version": "1.0.0"
}
```

**Common Issues**:
- ❌ **Azure OpenAI connection failed**: Check credentials in `ai_config.py`
- ❌ **Import errors**: Ensure all dependencies are copied to service directory
- ❌ **Port already in use**: Check if port 8001 is available

---

### 2. Search Service (Port 8002)

**Location**: `agents/search-service/`

**Start Command**:
```powershell
cd agents\search-service
python service.py
```

**Dependencies**:
- `search_service.py`
- `cache_manager.py`

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8002/health
```

**Common Issues**:
- ❌ **UAT data not found**: Check `data/uats.json` exists
- ❌ **Search returns no results**: Verify UAT data is properly formatted

---

### 3. Enhanced Matching (Port 8003)

**Location**: `agents/enhanced-matching/`

**Start Command**:
```powershell
cd agents\enhanced-matching
python service.py
```

**Dependencies**:
- Azure OpenAI (GPT-4)
- `enhanced_matching.py`
- `ai_config.py`
- `cache_manager.py`
- Azure DevOps (optional)

**Configuration**:
```python
# For Azure DevOps integration
AZURE_DEVOPS_ORG = "https://dev.azure.com/your-org"
AZURE_DEVOPS_PROJECT = "your-project"
```

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8003/health
```

**Common Issues**:
- ❌ **ADO authentication failed**: Check Azure DevOps credentials
- ⚠️  **Service starts without ADO**: This is OK, ADO is optional

---

### 4. UAT Management (Port 8004)

**Location**: `agents/uat-management/`

**Start Command**:
```powershell
cd agents\uat-management
python service.py
```

**Dependencies**:
- `uat_manager.py` (or local implementation)
- File storage for UATs

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8004/health
```

**Common Issues**:
- ❌ **Cannot create UAT**: Check write permissions on data directory
- ❌ **UAT ID collisions**: Ensure unique ID generation

---

### 5. LLM Classifier (Port 8005)

**Location**: `agents/llm-classifier/`

**Start Command**:
```powershell
cd agents\llm-classifier
python service.py
```

**Dependencies**:
- Azure OpenAI (GPT-4)
- `llm_classifier.py`
- `ai_config.py`
- `cache_manager.py`

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8005/health
```

**Test Classification**:
```powershell
$body = @{text = "I need help with Azure AD authentication"} | ConvertTo-Json
Invoke-WebRequest -Method POST -Uri "http://localhost:8005/classify" -Body $body -ContentType "application/json"
```

**Common Issues**:
- ❌ **High latency**: Check cache is working (should be <10ms for cached)
- ❌ **Low confidence scores**: Review system prompt in `llm_classifier.py`

---

### 6. Embedding Service (Port 8006)

**Location**: `agents/embedding-service/`

**Start Command**:
```powershell
cd agents\embedding-service
python service.py
```

**Dependencies**:
- Azure OpenAI (text-embedding-3-large)
- `embedding_service.py`
- `ai_config.py`
- `cache_manager.py`

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8006/health
```

**Test Embedding**:
```powershell
$body = @{text = "Test embedding generation"} | ConvertTo-Json
Invoke-WebRequest -Method POST -Uri "http://localhost:8006/embed" -Body $body -ContentType "application/json"
```

**Common Issues**:
- ❌ **Embedding API errors**: Check deployment name matches "text-embedding-3-large"
- ❌ **Cache growing too large**: Run `/cache/cleanup` endpoint

---

### 7. Vector Search (Port 8007)

**Location**: `agents/vector-search/`

**Start Command**:
```powershell
cd agents\vector-search
python service.py
```

**Dependencies**:
- `vector_search.py`
- `embedding_service.py`
- `cache_manager.py`
- `ai_config.py`
- sklearn, numpy

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8007/health
```

**Test Vector Search**:
```powershell
# Index test data
$items = @(
    @{id="test-1"; title="Test"; description="Test description"}
)
$body = @{collection_name="test"; items=$items} | ConvertTo-Json -Depth 10
Invoke-WebRequest -Method POST -Uri "http://localhost:8007/index" -Body $body -ContentType "application/json"

# Search
$searchBody = @{query="test"; collection_name="test"; top_k=5} | ConvertTo-Json
Invoke-WebRequest -Method POST -Uri "http://localhost:8007/search" -Body $searchBody -ContentType "application/json"
```

**Common Issues**:
- ❌ **Embedding Service not running**: Start Embedding Service first
- ❌ **Out of memory**: Large collections require more RAM

---

### 8. API Gateway (Port 8000)

**Location**: Root directory

**Start Command**:
```powershell
cd C:\Projects\Hack
python api_gateway.py
```

**Dependencies**:
- All gateway route modules in `gateway/routes/`
- httpx for proxying

**Health Check**:
```powershell
Invoke-WebRequest http://localhost:8000/health
```

**API Documentation**:
Open browser to: http://localhost:8000/docs

**Common Issues**:
- ❌ **Route not found**: Check service is running on expected port
- ❌ **Service unavailable (503)**: Backend service is down
- ❌ **Import errors**: Clear `__pycache__` directories

---

## ⚙️ Configuration

### AI Configuration (`ai_config.py`)

```python
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://your-instance.openai.azure.com/"
AZURE_OPENAI_KEY = "your-key-here"
AZURE_OPENAI_API_VERSION = "2024-08-01-preview"

# Model Deployments
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4-32k"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-3-large"

# Model Parameters
MAX_TOKENS = 4000
TEMPERATURE = 0.7
```

### Cache Configuration (`cache_manager.py`)

```python
# Cache Settings
CACHE_DIRECTORY = "cache/ai_cache"
CACHE_TTL_DAYS = 7
MAX_CACHE_SIZE_MB = 1000  # 1GB

# Cache Strategy
CACHE_STRATEGY = "api_first"  # or "cache_first"
```

### Service Ports

| Service | Port | Configurable In |
|---------|------|-----------------|
| Context Analyzer | 8001 | `agents/context-analyzer/service.py` |
| Search Service | 8002 | `agents/search-service/service.py` |
| Enhanced Matching | 8003 | `agents/enhanced-matching/service.py` |
| UAT Management | 8004 | `agents/uat-management/service.py` |
| LLM Classifier | 8005 | `agents/llm-classifier/service.py` |
| Embedding Service | 8006 | `agents/embedding-service/service.py` |
| Vector Search | 8007 | `agents/vector-search/service.py` |
| API Gateway | 8000 | `api_gateway.py` |

To change a port, edit the `uvicorn.run(app, host="0.0.0.0", port=XXXX)` line in the service file.

---

## 📊 Monitoring & Health Checks

### Individual Service Health
```powershell
# Check specific service
Invoke-WebRequest http://localhost:8001/health | ConvertFrom-Json

# Expected output:
# {
#   "status": "healthy",
#   "service": "context-analyzer",
#   "version": "1.0.0",
#   "uptime": 3600
# }
```

### All Services Health
```powershell
$services = @(
    @{name="Context Analyzer"; port=8001},
    @{name="Search Service"; port=8002},
    @{name="Enhanced Matching"; port=8003},
    @{name="UAT Management"; port=8004},
    @{name="LLM Classifier"; port=8005},
    @{name="Embedding Service"; port=8006},
    @{name="Vector Search"; port=8007},
    @{name="API Gateway"; port=8000}
)

foreach ($svc in $services) {
    try {
        $r = Invoke-WebRequest "http://localhost:$($svc.port)/health" -TimeoutSec 2
        Write-Host "✅ $($svc.name): HEALTHY" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($svc.name): DOWN" -ForegroundColor Red
    }
}
```

### Service Info
Each service provides detailed info:
```powershell
Invoke-WebRequest http://localhost:8001/info | ConvertFrom-Json
```

### Cache Statistics
Services with caching:
```powershell
# LLM Classifier
Invoke-WebRequest http://localhost:8005/cache/stats

# Embedding Service
Invoke-WebRequest http://localhost:8006/cache/stats
```

### Application Insights (Optional)
If configured, view metrics in Azure Portal:
- Request rates
- Response times
- Error rates
- Custom events

---

## 🔧 Troubleshooting

### Service Won't Start

**Symptom**: Service exits immediately or shows import errors

**Solutions**:
1. Check Python version: `python --version` (need 3.11+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check for port conflicts: `netstat -ano | findstr :8001`
4. Verify all shared modules are copied to service directory
5. Clear Python cache: `Remove-Item -Recurse __pycache__`

### Azure OpenAI Connection Failed

**Symptom**: "Authentication failed" or "Connection refused"

**Solutions**:
1. Verify credentials in `ai_config.py`
2. Check endpoint URL format (should end with `/`)
3. Verify API key is valid
4. Check deployment names match exactly
5. Test connection:
```powershell
$headers = @{
    "api-key" = "your-key"
}
Invoke-WebRequest -Headers $headers "https://your-instance.openai.azure.com/openai/deployments?api-version=2024-08-01-preview"
```

### Service Returns 503 (Service Unavailable)

**Symptom**: Gateway returns 503 when accessing service

**Solutions**:
1. Check backend service is running: `Invoke-WebRequest http://localhost:8001/health`
2. Verify port in gateway routes matches service port
3. Check service logs for errors
4. Restart backend service

### High Latency

**Symptom**: Requests take >5 seconds

**Solutions**:
1. Check if caching is working:
   - First request: 1-3s (API call)
   - Subsequent requests: <10ms (cache hit)
2. Verify Azure OpenAI region is close to deployment
3. Check network connectivity
4. Monitor Azure OpenAI rate limits

### Cache Not Working

**Symptom**: Every request is slow (no cache hits)

**Solutions**:
1. Verify cache directory exists: `ls cache/ai_cache`
2. Check cache file permissions
3. Review cache logs for errors
4. Check cache TTL settings
5. View cache stats: `Invoke-WebRequest http://localhost:8005/cache/stats`

### Out of Memory (Vector Search)

**Symptom**: Vector Search crashes with memory error

**Solutions**:
1. Reduce collection size
2. Clear collections: `Invoke-WebRequest -Method POST http://localhost:8007/collections/clear-all`
3. Increase available RAM
4. Consider migrating to FAISS for large collections

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'xxx'`

**Solutions**:
1. Ensure shared modules are in service directory:
```powershell
# Copy shared modules to service
Copy-Item ai_config.py agents/context-analyzer/
Copy-Item cache_manager.py agents/context-analyzer/
Copy-Item intelligent_context_analyzer.py agents/context-analyzer/
```

2. Check `requirements.txt` is installed:
```powershell
pip install -r agents/context-analyzer/requirements.txt
```

3. Verify Python path:
```powershell
python -c "import sys; print('\n'.join(sys.path))"
```

### Gateway Route Not Found (404)

**Symptom**: `/api/vector/search` returns 404

**Solutions**:
1. Check router is registered in `api_gateway.py`:
```python
from gateway.routes import vector_search
app.include_router(vector_search.router, prefix="/api/vector")
```

2. Clear gateway cache:
```powershell
Remove-Item -Recurse gateway/__pycache__
Remove-Item -Recurse gateway/routes/__pycache__
```

3. Restart API Gateway

### All Tests Failing

**Symptom**: `test_end_to_end.py` shows all failures

**Solutions**:
1. Ensure all services are running:
```powershell
.\start_all_services.ps1
```

2. Wait 30 seconds for services to fully initialize

3. Run health check script first

4. Check test configuration (ports, URLs)

---

## 🐳 Production Deployment

### Docker Deployment

Each service has a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy service files
COPY service.py .
COPY requirements.txt .
COPY *.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8001

# Run service
CMD ["python", "service.py"]
```

**Build Image**:
```bash
cd agents/context-analyzer
docker build -t gcs-context-analyzer:1.0 .
```

**Run Container**:
```bash
docker run -d \
  -p 8001:8001 \
  -e AZURE_OPENAI_ENDPOINT="https://..." \
  -e AZURE_OPENAI_KEY="..." \
  --name context-analyzer \
  gcs-context-analyzer:1.0
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  context-analyzer:
    build: ./agents/context-analyzer
    ports:
      - "8001:8001"
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
    networks:
      - gcs-network

  search-service:
    build: ./agents/search-service
    ports:
      - "8002:8002"
    networks:
      - gcs-network

  # ... other services ...

  api-gateway:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - context-analyzer
      - search-service
      # ... other services ...
    networks:
      - gcs-network

networks:
  gcs-network:
    driver: bridge
```

**Start All Services**:
```bash
docker-compose up -d
```

### Kubernetes Deployment

Create deployment manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: context-analyzer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: context-analyzer
  template:
    metadata:
      labels:
        app: context-analyzer
    spec:
      containers:
      - name: context-analyzer
        image: gcs-context-analyzer:1.0
        ports:
        - containerPort: 8001
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-openai-secret
              key: endpoint
        - name: AZURE_OPENAI_KEY
          valueFrom:
            secretKeyRef:
              name: azure-openai-secret
              key: api-key
---
apiVersion: v1
kind: Service
metadata:
  name: context-analyzer
spec:
  selector:
    app: context-analyzer
  ports:
  - port: 8001
    targetPort: 8001
  type: ClusterIP
```

**Deploy**:
```bash
kubectl apply -f k8s/
```

### Production Checklist

- [ ] Configure HTTPS/TLS
- [ ] Set up authentication (API keys, OAuth)
- [ ] Enable rate limiting
- [ ] Configure log aggregation (ELK, Azure Monitor)
- [ ] Set up monitoring dashboards
- [ ] Configure auto-scaling
- [ ] Set up backup and recovery
- [ ] Document runbook procedures
- [ ] Configure secrets management
- [ ] Set up CI/CD pipeline
- [ ] Perform load testing
- [ ] Set up disaster recovery
- [ ] Configure network policies
- [ ] Enable security scanning
- [ ] Set up alerts and notifications

---

## 📚 Additional Resources

- **Architecture Documentation**: `ARCHITECTURE.md`
- **Phase Summaries**: `PHASE_*_SUMMARY.md`
- **API Documentation**: http://localhost:8000/docs
- **Test Suites**: `test_*.py` files
- **Troubleshooting**: This guide + service logs

---

## 🆘 Support

**Common Commands**:
```powershell
# Stop all Python processes
Get-Process python | Stop-Process -Force

# Start all services
.\start_all_services.ps1

# Run end-to-end tests
python test_end_to_end.py

# Check service health
Invoke-WebRequest http://localhost:8000/health

# View API docs
Start-Process http://localhost:8000/docs
```

**Service Logs**:
Each service outputs logs to console. To save logs:
```powershell
python service.py > service.log 2>&1
```

---

**Last Updated**: January 17, 2026  
**Version**: 1.0  
**Tested On**: Windows 11, Python 3.13
