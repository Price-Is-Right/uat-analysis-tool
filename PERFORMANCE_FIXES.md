# Performance Fixes for "Window is Busy" Issues

## Problem Summary
The application experiences long pauses and "window is busy" messages due to:
1. ⏱️ Blocking subprocess calls (30-60 second timeouts)
2. 🌐 Sequential HTTP requests with delays
3. 🔄 Sequential service startup (60+ seconds)
4. ❌ No async operations or threading

## Root Causes Identified

### 1. Azure CLI Subprocess Calls (intelligent_context_analyzer.py)
**Lines 353-357**: Blocking subprocess with 30s timeout
```python
result = subprocess.run([
    r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd', 
    'account', 'list-locations'
], capture_output=True, text=True, timeout=30)  # ⚠️ BLOCKS FOR UP TO 30 SECONDS
```

### 2. Microsoft Learn API Calls (intelligent_context_analyzer.py)
**Lines 561-597**: Sequential requests with sleep delays
```python
response = requests.get(base_url, params={...}, timeout=5)  # ⚠️ BLOCKS FOR UP TO 5 SECONDS
time.sleep(0.2)  # ⚠️ ADDS 200ms PAUSE BETWEEN REQUESTS
```

### 3. Sequential Service Startup (start_all_services.ps1)
**Lines 13-106**: Starting services one-by-one
```powershell
Start-Process python -ArgumentList "$contextAnalyzerPath\service.py"
Start-Sleep -Seconds 8  # ⚠️ WAITS 8 SECONDS
$health = Invoke-WebRequest -Uri "http://localhost:8001/health"  # ⚠️ BLOCKS UNTIL RESPONSE
```

## Recommended Solutions

### Solution 1: Use Async/Threading for HTTP Requests
Replace sequential requests with concurrent execution:

```python
import concurrent.futures
import threading

def fetch_product_async(self, search_query, category, base_url):
    """Async product fetch"""
    try:
        response = requests.get(
            base_url,
            params={"search": search_query, "locale": "en-us", "$top": 3},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        return None

def _fetch_microsoft_products(self) -> Dict[str, Dict]:
    """Fetch products concurrently"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for search_query, category in product_searches:
            future = executor.submit(
                self.fetch_product_async, 
                search_query, 
                category, 
                base_url
            )
            futures.append((future, search_query, category))
        
        # Collect results without blocking individual requests
        for future, query, category in futures:
            result = future.result(timeout=6)  # Slightly longer than request timeout
            if result:
                # Process result...
```

### Solution 2: Cache-First Strategy with Background Refresh
Don't block on API calls - use cache immediately and update in background:

```python
def _fetch_microsoft_products(self) -> Dict[str, Dict]:
    """Use cached data immediately, refresh in background if needed"""
    
    # Check cache first
    cached_products = self._get_cached_data('microsoft_products')
    cache_age = self._get_cache_age('microsoft_products')
    
    # Return cached data immediately if available
    if cached_products and cache_age < 86400:  # Less than 24 hours
        return cached_products
    
    # If cache is old, start background refresh but return old cache
    if cached_products and cache_age >= 86400:
        # Start background thread to refresh cache
        threading.Thread(
            target=self._refresh_products_cache,
            daemon=True
        ).start()
        return cached_products  # Don't wait for refresh
    
    # Only if no cache at all, do synchronous fetch
    return self._fetch_products_from_api()
```

### Solution 3: Parallel Service Startup
Start all services simultaneously instead of sequentially:

```powershell
# start_all_services_parallel.ps1

Write-Host "🚀 Starting all GCS Services in parallel..." -ForegroundColor Green

# Define all services
$services = @(
    @{Name="Context Analyzer"; Port=8001; Path="C:\Projects\Hack\agents\context-analyzer"},
    @{Name="Search Service"; Port=8002; Path="C:\Projects\Hack\agents\search-service"},
    @{Name="Enhanced Matching"; Port=8003; Path="C:\Projects\Hack\agents\enhanced-matching"},
    @{Name="UAT Management"; Port=8004; Path="C:\Projects\Hack\agents\uat-management"},
    @{Name="LLM Classifier"; Port=8005; Path="C:\Projects\Hack\agents\llm-classifier"},
    @{Name="Embedding Service"; Port=8006; Path="C:\Projects\Hack\agents\embedding-service"},
    @{Name="Vector Search"; Port=8007; Path="C:\Projects\Hack\agents\vector-search"},
    @{Name="API Gateway"; Port=8000; Path="C:\Projects\Hack\gateway"}
)

# Start all services at once
$jobs = @()
foreach ($service in $services) {
    Write-Host "📊 Starting $($service.Name) on port $($service.Port)..." -ForegroundColor Cyan
    $process = Start-Process python -ArgumentList "$($service.Path)\service.py" `
        -NoNewWindow -WorkingDirectory $service.Path -PassThru
    $jobs += @{Name=$service.Name; Port=$service.Port; Process=$process}
}

# Wait a bit for services to initialize
Write-Host "`n⏳ Waiting for services to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check health of all services in parallel
$healthChecks = @()
foreach ($job in $jobs) {
    $healthChecks += Start-Job -ScriptBlock {
        param($port, $name)
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port/health" `
                -Method GET -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
            return @{Name=$name; Success=$true}
        } catch {
            return @{Name=$name; Success=$false}
        }
    } -ArgumentList $job.Port, $job.Name
}

# Wait for all health checks (max 10 seconds)
$healthChecks | Wait-Job -Timeout 10 | Receive-Job | ForEach-Object {
    if ($_.Success) {
        Write-Host "✅ $($_.Name) is healthy!" -ForegroundColor Green
    } else {
        Write-Host "❌ $($_.Name) failed to start!" -ForegroundColor Red
    }
}

$healthChecks | Remove-Job -Force
```

### Solution 4: Remove Azure CLI Dependency
Replace subprocess calls with Azure SDK for Python:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient

def _fetch_azure_regions_sdk(self) -> Dict[str, List[str]]:
    """Fetch Azure regions using Azure SDK (faster, no subprocess)"""
    try:
        credential = DefaultAzureCredential()
        subscription_client = SubscriptionClient(credential)
        
        locations = []
        for location in subscription_client.subscriptions.list_locations(
            subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID')
        ):
            locations.append({
                'name': location.name,
                'displayName': location.display_name
            })
        
        return self._process_regions(locations)
    except Exception as e:
        self.logger.warning(f"Azure SDK region fetch failed: {e}")
        return self._get_static_regions()
```

### Solution 5: Add Request Timeouts Everywhere
Ensure all blocking operations have short timeouts:

```python
# Current (blocks indefinitely)
response = requests.get(url)

# Fixed (times out after 3 seconds)
response = requests.get(url, timeout=3)

# Current subprocess (blocks up to 30s)
result = subprocess.run([...], timeout=30)

# Fixed (blocks only 5s)
result = subprocess.run([...], timeout=5)
```

## Priority Fixes

### 🔴 **High Priority (Immediate Impact)**
1. **Add threading to Microsoft Learn API calls** - Reduces 2-5 second pauses
2. **Use cache-first strategy** - Return cached data immediately
3. **Parallel service startup** - Reduces 60s startup to ~10s

### 🟡 **Medium Priority**
4. **Replace Azure CLI with SDK** - More reliable, faster
5. **Add progress indicators** - User feedback during operations

### 🟢 **Low Priority**
6. **Optimize cache management** - Better TTL strategy
7. **Add retry logic with exponential backoff**

## Testing the Fixes

After implementing fixes, verify:
- ✅ No "window is busy" messages during normal operation
- ✅ Application responds within 2-3 seconds
- ✅ Services start in parallel within 10 seconds
- ✅ Background tasks don't block UI/API responses

## Files to Modify

1. **intelligent_context_analyzer.py**
   - Lines 353-392: Replace subprocess with SDK or add threading
   - Lines 550-606: Add concurrent.futures for parallel requests
   - Lines 463-606: Implement cache-first strategy

2. **start_all_services.ps1**
   - Replace sequential startup with parallel jobs
   - Use background jobs for health checks

3. **app.py**
   - Add async route handlers for long operations
   - Implement progress tracking with WebSockets or SSE

## Expected Performance Improvements

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Product Fetch | 3-5s | 0.1s (cached) | 30-50x faster |
| Azure Regions | 30s | 0.1s (cached) or 2s (SDK) | 15-150x faster |
| Service Startup | 60-80s | 10-15s | 4-6x faster |
| Overall Response | 5-10s | 0.5-2s | 5-10x faster |
