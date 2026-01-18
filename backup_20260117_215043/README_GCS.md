# GCS Project - Getting Started Guide
**Welcome to the GCS (Global Customer Support) AI-Powered UAT Management System**

---

## What is GCS?

GCS is an intelligent platform that helps manage Unified Action Tracker (UAT) events through:
- **AI-powered analysis** of user-submitted issues
- **Automated search** for relevant documentation
- **Smart routing** to appropriate teams
- **Real-time analytics** and reporting

Built as a microservices architecture, GCS supports multiple web applications and integrates with Microsoft 365 Copilot.

---

## Documentation Index

### 📘 Architecture & Design
1. **[GCS_ARCHITECTURE.md](GCS_ARCHITECTURE.md)** - Complete system architecture
   - System overview and components
   - Data flow diagrams
   - Technology stack
   - Migration to Copilot strategy

2. **[INFRASTRUCTURE_PLAN.md](infrastructure/INFRASTRUCTURE_PLAN.md)** - Azure infrastructure
   - Resource specifications
   - Deployment steps
   - Security configuration
   - Cost estimates

3. **[PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)** - Implementation plan
   - Project structure
   - Phase-by-phase tasks
   - Timeline and milestones
   - Risk management

### 📗 Legacy Documentation (Archive)
- `AI_INTEGRATION_ARCHITECTURE.md` - Original AI integration design
- `AI_SETUP.md` - Setup instructions for current system
- `API_TESTING_GUIDE.md` - API testing procedures
- `DOCUMENTATION_INDEX.md` - Index of all docs
- `QUICKSTART.md` - Quick start for current system
- `START_APP.md` - How to run current Flask app
- `TECHNICAL_NOTES.md` - Technical implementation notes
- `TROUBLESHOOTING.md` - Common issues and solutions

---

## Current System (Monolithic Flask App)

### What We Have Today

**Single Flask Application:**
- `app.py` (2098 lines) - All routes and business logic
- Web interface for users to submit issues
- AI-powered context analysis
- Vector search for documentation
- Azure DevOps integration for UAT creation

**Core Components:**
- `intelligent_context_analyzer.py` - AI analysis engine
- `search_service.py` - Search orchestration
- `vector_search.py` - Vector similarity search
- `hybrid_context_analyzer.py` - Hybrid search strategies
- `llm_classifier.py` - LLM classification
- `embedding_service.py` - Generate embeddings
- `ado_integration.py` - Azure DevOps API
- `enhanced_matching.py` - Matching algorithms

**Data Storage:**
- Local JSON files (not container-friendly):
  - `context_evaluations.json` - User feedback
  - `corrections.json` - System corrections
  - `retirements.json` - Product retirements
  - `issues_actions.json` - Issue categories

### What's Working ✅
- User can submit issues through wizard
- AI analyzes and detects Microsoft products
- Search finds relevant UATs from Azure DevOps
- Can create work items in Azure DevOps
- Product detection is dynamic (no hardcoded lists)
- Smart filtering of action verbs

### What's Needed ⚠️
- Support multiple web apps (user + triage team)
- Scale agents independently
- Container-friendly storage (not local files)
- Better metrics and analytics
- Routing capabilities for triage team
- Production-ready infrastructure

---

## Target System (Microservices Architecture)

### What We're Building

**Multi-Application Platform:**
- **User Submission Web App** - End users create UAT events
- **Triage Management Web App** - Team routes and manages UATs
- **Analytics Dashboard** - Leadership visibility (future)

**API Gateway Layer:**
- Central routing for all applications
- Handles authentication and data access
- Orchestrates agent calls

**Microservices (Agents):**
- **Context Analyzer** - AI-powered analysis
- **Search Agent** - Multi-strategy search
- **Routing Agent** - Team assignment (new)
- **Rules Agent** - Validation and policies (new)
- **Analytics Agent** - Metrics and reporting (new)
- **Communications Agent** - Notifications (new)
- **ADO Integration** - Work item management
- **LLM Classifier** - AI classification
- **Vector Service** - Embeddings

**Cloud Storage:**
- **Azure Blob Storage** - All data (replaces JSON files)
- **Application Insights** - Metrics and monitoring
- **Azure OpenAI** - AI services (existing)
- **Key Vault** - Secrets management

### Why Microservices?

1. **Multiple Apps** - User app and triage app share same agents
2. **Independent Scaling** - Scale busy agents without affecting others
3. **Container-Ready** - No local file dependencies
4. **Copilot Migration** - Move one agent at a time to M365 Copilot
5. **Team Agility** - Work on agents independently

---

## Getting Started

### For Developers

#### Current System (Before Migration)

1. **Prerequisites:**
   ```bash
   Python 3.11+
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

3. **Run Application:**
   ```bash
   python app.py
   # or
   .\start_app.ps1
   ```

4. **Access:**
   - Web UI: http://localhost:5000
   - Debug logs: debug_context.log, debug_ica.log

#### New System (After Migration)

1. **Prerequisites:**
   ```bash
   Docker Desktop
   Azure CLI
   kubectl (for Container Apps)
   ```

2. **Local Development:**
   ```bash
   docker-compose up
   # Starts all agents and API Gateway locally
   ```

3. **Deploy to Azure:**
   ```bash
   cd infrastructure/scripts
   ./deploy-infrastructure.sh
   ```

4. **Access:**
   - User Web App: https://ca-user-webapp-dev.northcentralus.azurecontainerapps.io
   - Triage Web App: https://ca-triage-webapp-dev.northcentralus.azurecontainerapps.io
   - API Gateway: https://ca-api-gateway-dev.northcentralus.azurecontainerapps.io
   - API Docs: https://ca-api-gateway-dev.northcentralus.azurecontainerapps.io/docs

---

## Implementation Status

### ✅ Phase 0: Planning & Documentation (Current)
- [x] Architecture documentation
- [x] Infrastructure plan
- [x] Project roadmap
- [ ] Team review and approval

### ⏭️ Phase 1: Infrastructure Setup (Next)
- [ ] Create Azure resource group
- [ ] Provision storage, App Insights, Container Apps
- [ ] Setup Key Vault and secrets
- **Estimated:** 2-3 days

### ⏭️ Phase 2-10: Development & Deployment
- See [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for detailed breakdown
- **Estimated:** 6-8 weeks total

### 🔮 Phase 11: Copilot Migration (Future)
- After stable production deployment
- Incremental agent-by-agent migration

---

## Quick Reference

### Key Resources

**Azure Resources (Development):**
- Resource Group: `rg-gcs-dev`
- Region: North Central US
- Storage: `stgcsdev001`
- App Insights: `appi-gcs-dev`
- Container Registry: `acrgcsdev001`
- Key Vault: `kv-gcs-dev-001`

**Azure OpenAI (Existing):**
- Resource: `OpenAI-bp-NorthCentral`
- Models: gpt-4o, text-embedding-3-large
- Region: North Central US

**Azure DevOps:**
- Organization: (configured in environment)
- Project: (configured in environment)

### Important Files

**Current System:**
- `app.py` - Main Flask application
- `intelligent_context_analyzer.py` - Core AI logic
- `.env` - Environment configuration
- `context_evaluations.json` - User feedback data

**New System:**
- `GCS_ARCHITECTURE.md` - System design
- `PROJECT_ROADMAP.md` - Implementation plan
- `infrastructure/INFRASTRUCTURE_PLAN.md` - Azure setup
- `docker-compose.yml` - Local development (to be created)

### Environment Variables

**Current (`.env`):**
```
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT=gpt-4o
AZURE_DEVOPS_ORG=...
AZURE_DEVOPS_PROJECT=...
AZURE_DEVOPS_PAT=...
```

**Future (Key Vault):**
All secrets moved to Azure Key Vault, accessed via managed identity.

---

## Common Tasks

### Run Current App Locally
```bash
python app.py
```

### Run Tests
```bash
# Currently minimal tests exist
python -m pytest tests/
```

### View Logs
```bash
# Local development
tail -f debug_context.log
tail -f debug_ica.log

# Azure (after migration)
az containerapp logs show --name ca-context-analyzer-dev --resource-group rg-gcs-dev
```

### Access Azure Portal
1. Login: https://portal.azure.com
2. Navigate to Resource Group: `rg-gcs-dev`
3. View resources and metrics

### Query Application Insights
1. Open App Insights: `appi-gcs-dev`
2. Go to "Logs"
3. Use KQL queries:
```kql
customEvents
| where timestamp > ago(24h)
| where name == "AnalysisCompleted"
| summarize count() by bin(timestamp, 1h)
```

---

## Need Help?

### Documentation
- **Architecture:** See [GCS_ARCHITECTURE.md](GCS_ARCHITECTURE.md)
- **Infrastructure:** See [infrastructure/INFRASTRUCTURE_PLAN.md](infrastructure/INFRASTRUCTURE_PLAN.md)
- **Roadmap:** See [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (legacy)

### Support Contacts
- **Owner:** bprice@microsoft.com
- **Azure Subscription:** MCAPS-Hybrid-REQ-53439-2023-bprice

### Resources
- Azure OpenAI Docs: https://learn.microsoft.com/azure/ai-services/openai/
- Azure Container Apps: https://learn.microsoft.com/azure/container-apps/
- Azure Blob Storage: https://learn.microsoft.com/azure/storage/blobs/
- FastAPI: https://fastapi.tiangolo.com/

---

## What's Next?

**Immediate (This Week):**
1. Review and approve architecture documentation
2. Create Azure infrastructure (Phase 1)
3. Migrate data to Blob Storage (Phase 2)

**Short Term (Next 2-4 Weeks):**
1. Build API Gateway
2. Extract Context Analyzer and Search agents
3. Refactor user web app

**Medium Term (Next 1-2 Months):**
1. Build new agents (routing, rules, analytics, comms)
2. Build triage web app
3. Production deployment

**Long Term (Future):**
1. Analytics dashboard
2. Microsoft 365 Copilot integration
3. Additional features based on feedback

---

**Document Version:** 1.0  
**Last Updated:** January 17, 2026  
**Status:** Active Development

---

**Welcome to GCS!** 🚀
