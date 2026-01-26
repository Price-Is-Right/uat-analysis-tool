# Project Status - Intelligent Context Analysis System
**Last Updated**: January 23, 2026, 10:30 PM
**Status**: ✅ All systems operational

---

## Current Architecture

### Main Application
- **Web UI**: http://localhost:5003
- **Teams Bot**: http://localhost:3978/api/messages
- **Startup Script**: `.\start_app.ps1` (starts everything)

### Microservices (All ports working)
- API Gateway: 8000
- Context Analyzer: 8001
- Search Service: 8002
- Enhanced Matching: 8003
- UAT Management: 8004
- LLM Classifier: 8005
- Embedding Service: 8006
- Vector Search: 8007
- **Admin Portal: 8008** ⬅️ NEW

---

## Recent Changes (Jan 23, 2026)

### 1. **TFT Feature Search Fixes** ✅
- **Issue**: `'NoneType' object has no attribute 'search_tft_features'`
- **Fix**: Changed to use `get_ado_client()` for proper initialization
- **Location**: `app.py` line ~1634

### 2. **Azure OpenAI Timeout Fix** ✅
- **Issue**: Application hanging on embedding API calls
- **Fix**: Added 10-second timeout to AzureOpenAI client
- **Location**: `embedding_service.py` line ~30

### 3. **Dual Authentication Caching** ✅
- **Issue**: Two auth prompts every time (not cached)
- **Fix**: Added caching for both main + TFT credentials
- **Locations**: 
  - `ado_integration.py` lines 60-65 (credential variables)
  - `ado_integration.py` lines 140-170 (TFT credential caching)
- **Result**: Only 2 prompts on first run (expected), then cached

### 4. **Admin Portal Port Change** ✅
- **Issue**: Port 8004 conflict with UAT Management
- **Fix**: Moved admin portal to port 8008
- **Files Modified**: 
  - `admin_service.py` (port change)
  - `start_admin_service.ps1` (port + URLs)
  - `start_app.ps1` (integrated admin portal startup)

---

## Known Working Features

✅ Web UI with Quick ICA analysis
✅ Teams Bot integration
✅ TFT Feature search for feature_request category
✅ Azure OpenAI context analysis
✅ Dual organization authentication (main + TFT)
✅ Embedding service with cache fallback
✅ All 7 microservices + API Gateway
✅ Admin portal on port 8008

---

## Known Issues

⚠️ Admin portal shows "AuthorizationFailure" on blob storage access
- Error: "This request is not authorized to perform this operation"
- Likely needs managed identity or storage permissions fix
- Workaround: Use local JSON files for testing

---

## Authentication Architecture

### Two Separate Organizations
1. **Main Org** (`unifiedactiontrackertest`)
   - Purpose: Work item creation
   - Method: Azure CLI or Interactive Browser
   - Cached in: `AzureDevOpsConfig._cached_credential`

2. **TFT Org** (`unifiedactiontracker/Technical Feedback`)
   - Purpose: Feature search
   - Method: Interactive Browser with MS tenant ID
   - Cached in: `AzureDevOpsConfig._cached_tft_credential`

Both prompt once on first use, then cached for session.

---

## Key Configuration

### Azure OpenAI
- Endpoint: Loaded from Key Vault
- Models:
  - Classification: `gpt-4o-02`
  - Embeddings: `text-embedding-3-large`
- Timeout: 10 seconds (prevents hanging)

### Caching Strategy
- Cache TTL: 7 days
- Location: `cache/ai_cache/`
- Behavior: Use cache directly if < 3 days old

---

## Recent Backups

1. **backup_tft_auth_fixes_20260123_220315/** 
   - TFT authentication fixes
   - Timeout fixes
   - Pre-admin portal changes

2. **backup_admin_portal_8008_20260123_222155/** ⬅️ LATEST
   - All TFT fixes
   - Admin portal on 8008
   - Integrated into start_app.ps1
   - Full code documentation

---

## Important Files

### Core Application
- `app.py` - Main Flask web application
- `start_app.ps1` - Startup script for all services
- `ado_integration.py` - Azure DevOps integration with dual auth
- `embedding_service.py` - Azure OpenAI embeddings with timeout

### Configuration
- `ai_config.py` - Azure OpenAI configuration
- `keyvault_config.py` - Azure Key Vault integration
- `.env` - Local environment variables (not in git)

### Microservices
- `api_gateway.py` - Central routing (port 8000)
- `agents/*/service.py` - Individual microservices

### Admin
- `admin_service.py` - Admin portal (port 8008)
- `start_admin_service.ps1` - Admin portal startup

---

## Next Steps / TODO

- [ ] Fix admin portal blob storage authorization
- [ ] Consider adding credential refresh logic for long sessions
- [ ] Monitor embedding API call patterns for optimization
- [ ] Add more comprehensive error handling for Azure OpenAI failures
- [ ] Document the full TFT search flow in architecture docs

---

## How to Start

```powershell
# Start everything (recommended)
.\start_app.ps1

# Start admin portal only (if needed separately)
.\start_admin_service.ps1

# Start individual services
cd agents\context-analyzer
python service.py
```

---

## Troubleshooting Quick Reference

### "NoneType has no attribute"
- Issue: ADO client not initialized
- Fix: Use `get_ado_client()` instead of global `ado_client`

### Application Hanging
- Issue: Azure OpenAI timeout not set
- Fix: Already fixed - 10 second timeout in embedding_service.py

### Multiple Auth Prompts
- Issue: Credentials not cached
- Fix: Already fixed - both credentials now cached

### Port Conflicts
- Issue: Service already running on port
- Solution: Check port assignments in start_app.ps1
- Admin portal: 8008 (moved from 8004)

---

**STATUS**: System is stable and working. All major issues from today resolved and documented.
