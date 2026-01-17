# GCS Infrastructure Deployment Plan
**Date:** January 17, 2026  
**Environment:** Development  
**Region:** North Central US

---

## Resource Group

**Name:** `rg-gcs-dev`  
**Location:** North Central US  
**Tags:**
- Environment: Development
- Project: GCS
- Owner: bprice@microsoft.com
- Purpose: AI-Powered UAT Management System

---

## Resources to Create

### 1. Storage Account
**Name:** `stgcsdev001`  
**Type:** StorageV2 (general purpose v2)  
**Replication:** LRS (Locally Redundant Storage)  
**Performance:** Standard  
**Access Tier:** Hot  
**Purpose:** Blob storage for evaluations, submissions, analyses

**Containers:**
- `gcs-data` (main data container)
  - Subdirectories: evaluations/, submissions/, analyses/, uat-created/, system/

**Estimated Cost:** ~$2-5/month (for dev usage)

---

### 2. Application Insights
**Name:** `appi-gcs-dev`  
**Type:** Application Insights  
**Workspace:** Create new Log Analytics workspace `log-gcs-dev`  
**Purpose:** Metrics, events, monitoring, dashboards

**What Gets Tracked:**
- Custom Events: SubmissionReceived, AnalysisCompleted, UATCreated, SearchCompleted
- Dependencies: Azure OpenAI, Azure DevOps API calls
- Requests: API Gateway calls
- Performance: Response times, error rates

**Estimated Cost:** Free tier (5GB/month) - likely $0/month

---

### 3. Container Registry
**Name:** `acrgcsdev001`  
**SKU:** Basic  
**Purpose:** Store Docker images for microservices and web apps

**Images to Host:**
- `gcs-api-gateway:latest`
- `gcs-context-analyzer:latest`
- `gcs-search-agent:latest`
- `gcs-routing-agent:latest`
- `gcs-rules-agent:latest`
- `gcs-analytics-agent:latest`
- `gcs-comms-agent:latest`
- `gcs-user-webapp:latest`
- `gcs-triage-webapp:latest`

**Estimated Cost:** ~$5/month

---

### 4. Container Apps Environment
**Name:** `cae-gcs-dev`  
**Type:** Azure Container Apps Environment  
**Workload Profile:** Consumption  
**Networking:** Public endpoint (dev), private in prod  
**Purpose:** Host all microservices and web apps

**Estimated Cost:** ~$0-20/month (pay per use)

---

### 5. Key Vault
**Name:** `kv-gcs-dev-001`  
**SKU:** Standard  
**Purpose:** Secure secrets management

**Secrets to Store:**
- `azure-openai-api-key`
- `azure-openai-endpoint`
- `azure-devops-pat`
- `storage-connection-string`
- `app-insights-instrumentation-key`

**Estimated Cost:** ~$0-1/month

---

### 6. Existing Resources (Reuse)
**Azure OpenAI Service:**
- Name: `OpenAI-bp-NorthCentral`
- Location: North Central US
- Models: gpt-4o, text-embedding-3-large
- Status: ✅ Already exists

---

## Network Architecture (Dev)

```
Internet
    │
    ├─────> User Web App (Public endpoint)
    │         ↓
    ├─────> Triage Web App (Public endpoint)
    │         ↓
    └─────> API Gateway (Public endpoint)
                ↓
          [Container Apps Environment]
                │
                ├─── Context Analyzer Agent
                ├─── Search Agent
                ├─── Routing Agent
                ├─── Rules Agent
                ├─── Analytics Agent
                ├─── Communications Agent
                ├─── ADO Integration Agent
                ├─── LLM Classifier Agent
                └─── Vector Service Agent
                      ↓
          [Azure Services]
                ├─── Blob Storage
                ├─── App Insights
                ├─── Azure OpenAI
                ├─── Key Vault
                └─── Azure DevOps
```

**Note:** Production will use private endpoints and VNET integration

---

## Security Configuration

### Storage Account
- Enable HTTPS only
- Minimum TLS version: 1.2
- Allow Azure services access
- Enable blob versioning
- Enable soft delete (7 days)

### Key Vault
- Enable RBAC
- Grant access to Container Apps managed identity
- Enable audit logging
- Soft delete: 90 days

### Container Apps
- Use managed identity for auth
- No storage of secrets in environment variables
- Pull secrets from Key Vault
- Enable logging to App Insights

### API Gateway
- Implement rate limiting
- API key authentication (dev)
- OAuth 2.0 / Azure AD (prod)
- Request validation

---

## Naming Conventions

**Pattern:** `{resource-type}-gcs-{environment}-{instance}`

Examples:
- Resource Group: `rg-gcs-dev`
- Storage Account: `stgcsdev001` (no hyphens, global unique)
- App Insights: `appi-gcs-dev`
- Container Apps Env: `cae-gcs-dev`
- Container App: `ca-context-analyzer-dev`
- Key Vault: `kv-gcs-dev-001` (3-24 chars, globally unique)
- Container Registry: `acrgcsdev001` (alphanumeric only)

**Resource Type Abbreviations:**
- rg = Resource Group
- st = Storage Account
- appi = Application Insights
- log = Log Analytics Workspace
- cae = Container Apps Environment
- ca = Container App
- kv = Key Vault
- acr = Azure Container Registry

---

## Deployment Steps

### Step 1: Create Resource Group ✅
```bash
az group create \
  --name rg-gcs-dev \
  --location northcentralus \
  --tags Environment=Development Project=GCS Owner=bprice@microsoft.com
```

### Step 2: Create Storage Account
```bash
az storage account create \
  --name stgcsdev001 \
  --resource-group rg-gcs-dev \
  --location northcentralus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot \
  --https-only true \
  --min-tls-version TLS1_2 \
  --enable-hierarchical-namespace false
```

### Step 3: Create Blob Container
```bash
az storage container create \
  --name gcs-data \
  --account-name stgcsdev001 \
  --auth-mode login
```

### 4. Create Log Analytics Workspace & Application Insights
```bash
# Create Log Analytics Workspace first
az monitor log-analytics workspace create \
  --resource-group rg-gcs-dev \
  --workspace-name log-gcs-dev \
  --location northcentralus \
  --retention-time 730 \
  --tags Environment=Development Project=GCS Purpose="Centralized logging and security audit"

# Create App Insights linked to Log Analytics
az monitor app-insights component create \
  --app appi-gcs-dev \
  --location northcentralus \
  --resource-group rg-gcs-dev \
  --workspace log-gcs-dev \
  --retention-time 730

# Enable diagnostic settings for comprehensive logging
az monitor diagnostic-settings create \
  --name gcs-diagnostics \
  --resource <resource-id> \
  --workspace log-gcs-dev \
  --logs '[{"category":"Audit","enabled":true},{"category":"Security","enabled":true}]'
```

### Step 5: Create Container Registry
```bash
az acr create \
  --name acrgcsdev001 \
  --resource-group rg-gcs-dev \
  --location northcentralus \
  --sku Basic \
  --admin-enabled true
```

### Step 6: Create Container Apps Environment
```bash
az containerapp env create \
  --name cae-gcs-dev \
  --resource-group rg-gcs-dev \
  --location northcentralus \
  --logs-workspace-id <log-workspace-id>
```

### Step 7: Create Key Vault
```bash
az keyvault create \
  --name kv-gcs-dev-001 \
  --resource-group rg-gcs-dev \
  --location northcentralus \
  --enable-rbac-authorization true
```

### Step 8: Store Secrets in Key Vault
```bash
# Get current Azure OpenAI info from environment
az keyvault secret set \
  --vault-name kv-gcs-dev-001 \
  --name azure-openai-api-key \
  --value <from-env-or-portal>

az keyvault secret set \
  --vault-name kv-gcs-dev-001 \
  --name azure-openai-endpoint \
  --value <from-env-or-portal>

# Storage connection string (after storage account created)
az keyvault secret set \
  --vault-name kv-gcs-dev-001 \
  --name storage-connection-string \
  --value <from-storage-account>

# App Insights instrumentation key
az keyvault secret set \
  --vault-name kv-gcs-dev-001 \
  --name app-insights-instrumentation-key \
  --value <from-app-insights>
```

---

## Migration from Current System

### Data Migration
**Current:** Local JSON files in project directory
- `context_evaluations.json`
- `corrections.json`
- `retirements.json`
- `issues_actions.json`

**Target:** Azure Blob Storage

**Migration Script:**
```python
# migrate_to_blob.py
from azure.storage.blob import BlobServiceClient
import json

conn_str = "<from-key-vault>"
blob_service = BlobServiceClient.from_connection_string(conn_str)
container = blob_service.get_container_client("gcs-data")

# Migrate evaluations
with open('context_evaluations.json') as f:
    data = json.load(f)
    for eval in data['evaluations']:
        blob_name = f"evaluations/{eval['timestamp'][:10].replace('-','/')}/eval-{eval['id']}.json"
        container.upload_blob(blob_name, json.dumps(eval), overwrite=True)

# Migrate system files
for filename in ['corrections.json', 'retirements.json', 'issues_actions.json']:
    with open(filename) as f:
        blob_name = f"system/{filename}"
        container.upload_blob(blob_name, f.read(), overwrite=True)
```

### Environment Variables
**Current:** `.env` file in project root
**Target:** Key Vault secrets

**Migration:** Move all secrets to Key Vault, use managed identity for access

---

## Cost Estimate (Development)

| Resource | SKU/Tier | Estimated Cost |
|----------|----------|----------------|
| Storage Account | Standard LRS | $2-5/month |
| Log Analytics Workspace | 730-day retention, ~5GB/day | $30-60/month |
| Application Insights | 730-day retention | $10-30/month |
| Container Registry | Standard (performance) | $20/month |
| Container Apps Environment | Consumption | $20-50/month |
| Container Apps (9 instances) | 1 CPU, 2GB RAM each (performance) | $100-200/month |
| Key Vault | Standard | $1-2/month |
| Azure Sentinel (optional) | SIEM/SOAR for security | $0-50/month |
| Azure OpenAI | Existing resource | $0 additional |
| **Total** | | **$183-417/month** |

**Note:** Cost optimized for performance, 2-year analytics retention, and comprehensive security logging for compliance. Production costs will scale with usage. Azure Sentinel optional but recommended for production security monitoring.

---

## Production Migration Checklist

When ready to move to production:

- [ ] Export ARM/Bicep templates
- [ ] Parameterize all environment-specific values
- [ ] Create `rg-gcs-prod` resource group
- [ ] Deploy production resources with `-prod` suffix
- [ ] Update all connection strings and endpoints
- [ ] Copy data from dev Blob Storage to prod
- [ ] Test all integrations
- [ ] Update DNS records
- [ ] Enable production-grade security (VNET, private endpoints)
- [ ] Setup production monitoring and alerting
- [ ] Document rollback procedure
- [ ] Perform load testing
- [ ] Schedule maintenance window
- [ ] Execute cutover plan
- [ ] Monitor for 24 hours
- [ ] Document lessons learned

---

## Next Actions

1. ✅ Create `GCS_ARCHITECTURE.md` - High-level architecture documentation
2. ✅ Create `INFRASTRUCTURE_PLAN.md` - Detailed infrastructure plan (this file)
3. ⏭️ Create Azure resource group via portal or Azure tools
4. ⏭️ Provision all infrastructure resources
5. ⏭️ Setup Key Vault and store secrets
6. ⏭️ Create project structure for microservices
7. ⏭️ Extract first agent (Context Analyzer)
8. ⏭️ Create API Gateway scaffold
9. ⏭️ Deploy to Container Apps

---

**Document Version:** 1.0  
**Last Updated:** January 17, 2026  
**Status:** Ready for Deployment
