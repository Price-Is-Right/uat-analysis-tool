# GCS (Global Customer Support) Architecture
**Project:** AI-Powered UAT Management & Triage System  
**Date:** January 17, 2026  
**Version:** 2.0 - Microservices Architecture

---

## Executive Summary

The GCS system is an AI-powered platform for managing Unified Action Tracker (UAT) events through intelligent analysis, automated triage, and multi-channel access. Built as a microservices architecture, it supports multiple web applications and can integrate with Microsoft 365 Copilot agents.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEB APPLICATIONS LAYER                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  User Submission │  │  Triage Mgmt     │  │  Analytics       │ │
│  │  Web App         │  │  Web App         │  │  Dashboard       │ │
│  │  (Flask/React)   │  │  (Flask/React)   │  │  (Future)        │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │
└───────────┼──────────────────────┼──────────────────────┼───────────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                         API GATEWAY LAYER                              │
│           Routes requests, manages auth, handles data access           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
│  │  Request       │  │  Agent         │  │  Data Access   │         │
│  │  Router        │  │  Orchestrator  │  │  Manager       │         │
│  └────────────────┘  └────────────────┘  └────────────────┘         │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                      MICROSERVICES (AGENT) LAYER                       │
│                    Each agent = independent container                  │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ Context         │  │ Search          │  │ Routing         │      │
│  │ Analyzer        │  │ Agent           │  │ Agent           │      │
│  │ Agent           │  │                 │  │ (New)           │      │
│  │                 │  │ - Vector Search │  │                 │      │
│  │ - AI Analysis   │  │ - Hybrid Search │  │ - Team Routing  │      │
│  │ - Product Det.  │  │ - Embeddings    │  │ - Priority      │      │
│  │ - Category ID   │  │                 │  │ - SLA Calc      │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ Rules           │  │ Analytics       │  │ Communications  │      │
│  │ Agent           │  │ Agent           │  │ Agent           │      │
│  │ (New)           │  │ (New)           │  │ (New)           │      │
│  │                 │  │                 │  │                 │      │
│  │ - Business Rules│  │ - Metrics       │  │ - Notifications │      │
│  │ - Validation    │  │ - Reporting     │  │ - Alerts        │      │
│  │ - Policy Enf.   │  │ - Trends        │  │ - Updates       │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ ADO Integration │  │ LLM Classifier  │  │ Vector Service  │      │
│  │ Agent           │  │ Agent           │  │ Agent           │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼────────────────────────────────────┐
│                        SHARED DATA & SERVICES LAYER                    │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ Azure Blob      │  │ Application     │  │ Azure OpenAI    │      │
│  │ Storage         │  │ Insights        │  │                 │      │
│  │                 │  │                 │  │ - GPT-4o        │      │
│  │ - Evaluations   │  │ - Metrics       │  │ - Embeddings    │      │
│  │ - Submissions   │  │ - Events        │  │ - Analysis      │      │
│  │ - Analysis      │  │ - Dashboards    │  │                 │      │
│  │ - System Data   │  │ - Alerts        │  │                 │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ Azure DevOps    │  │ Key Vault       │  │ Container       │      │
│  │ Integration     │  │                 │  │ Registry        │      │
│  │                 │  │ - Secrets       │  │                 │      │
│  │ - Work Items    │  │ - API Keys      │  │ - Agent Images  │      │
│  │ - Queries       │  │ - Connections   │  │ - Web App Images│      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
└───────────────────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. Web Applications Layer

**Purpose:** User-facing interfaces for different personas

#### A. User Submission Web App (Current - Being Refactored)
- **Purpose:** End users submit UAT events
- **Features:**
  - Guided wizard for issue submission
  - AI-powered analysis preview
  - Search existing documentation
  - Create Azure DevOps work items
  - View analysis details
- **Technology:** Flask + HTML/Bootstrap
- **Status:** Existing - needs API layer extraction

#### B. Triage Management Web App (New)
- **Purpose:** Triage team manages incoming UATs
- **Features:**
  - View all incoming UATs
  - See original AI analysis
  - Route to appropriate teams (support, capacity, dev, marketing)
  - Override AI recommendations
  - Track routing history
  - View analytics and metrics
- **Technology:** Flask + React (recommended)
- **Status:** Planned

#### C. Analytics Dashboard (Future)
- **Purpose:** Leadership visibility into UAT trends
- **Features:**
  - Real-time metrics
  - Product trend analysis
  - Team performance
  - SLA tracking
- **Technology:** React + Power BI / Grafana
- **Status:** Future phase

---

### 2. API Gateway Layer

**Purpose:** Central routing, orchestration, and data access for all applications

**Responsibilities:**
- Route requests to appropriate microservices
- Handle authentication and authorization
- Aggregate responses from multiple agents
- Manage shared data access (Blob Storage, App Insights)
- Provide consistent API contracts
- Handle retries and circuit breaking

**Technology:** FastAPI (Python) or Azure API Management

**Endpoints:**
```
POST /api/analyze         - Context analysis
POST /api/search          - Search operations
POST /api/route           - Routing decisions
GET  /api/evaluations     - Retrieve evaluations
POST /api/uat/create      - Create UAT work item
GET  /api/metrics         - Analytics data
```

---

### 3. Microservices (Agent) Layer

Each agent is an independent, containerized microservice with a specific responsibility.

#### A. Context Analyzer Agent ✅ (Existing Logic)
**Source:** `intelligent_context_analyzer.py`
**Purpose:** AI-powered analysis of user issues
**Capabilities:**
- Product detection (Azure services, Microsoft 365, etc.)
- Category classification
- Impact assessment
- Confidence scoring
- Reasoning explanation
**Input:** `{ "text": "...", "context": {...} }`
**Output:** `{ "analysis": {...}, "products": [...], "categories": [...], "confidence": 0.85 }`
**Technology:** Azure OpenAI GPT-4o
**Deployment:** Azure Container App

#### B. Search Agent ✅ (Existing Logic)
**Source:** `search_service.py`, `vector_search.py`, `hybrid_context_analyzer.py`
**Purpose:** Multi-strategy search for relevant documentation
**Capabilities:**
- Vector similarity search (embeddings)
- Keyword search (Azure DevOps)
- Hybrid search strategies
- Result ranking and scoring
**Input:** `{ "query": "...", "products": [...], "strategy": "hybrid" }`
**Output:** `{ "matches": [...], "total": 15, "scores": [...] }`
**Technology:** Azure OpenAI Embeddings, Azure DevOps API
**Deployment:** Azure Container App

#### C. Routing Agent 🆕 (New)
**Purpose:** Intelligent routing of UATs to appropriate teams
**Capabilities:**
- Team assignment (support, capacity, dev, marketing)
- Priority calculation
- SLA determination
- Escalation rules
- Load balancing across team members
**Input:** `{ "uat": {...}, "analysis": {...}, "context": {...} }`
**Output:** `{ "team": "support", "priority": "high", "sla_hours": 24, "assignee": "..." }`
**Technology:** Rule engine + ML classification
**Deployment:** Azure Container App

#### D. Rules Agent 🆕 (New)
**Purpose:** Business rules and policy enforcement
**Capabilities:**
- Validation rules
- Approval workflows
- Policy compliance checks
- Data quality enforcement
**Input:** `{ "action": "...", "data": {...}, "context": {...} }`
**Output:** `{ "valid": true, "violations": [], "recommendations": [...] }`
**Technology:** Python rules engine (durable-rules or similar)
**Deployment:** Azure Container App

#### E. Analytics Agent 🆕 (New)
**Purpose:** Generate metrics, reports, and insights
**Capabilities:**
- Real-time metric calculation
- Trend analysis
- Report generation
- Anomaly detection
**Input:** `{ "metric": "uat_creation_rate", "period": "30d", "filters": {...} }`
**Output:** `{ "value": 0.75, "trend": "increasing", "insights": [...] }`
**Technology:** Python analytics + Application Insights queries
**Deployment:** Azure Container App

#### F. Communications Agent 🆕 (New)
**Purpose:** Handle notifications and updates
**Capabilities:**
- Email notifications
- Teams messages
- Slack integration
- Status updates
- Escalation alerts
**Input:** `{ "event": "uat_created", "recipients": [...], "data": {...} }`
**Output:** `{ "sent": true, "delivery_status": {...} }`
**Technology:** Microsoft Graph API, SendGrid, Teams SDK
**Deployment:** Azure Container App

#### G. ADO Integration Agent ✅ (Existing Logic)
**Source:** `ado_integration.py`
**Purpose:** Azure DevOps work item management
**Capabilities:**
- Create work items
- Update work items
- Query work items
- Link related items
**Technology:** Azure DevOps REST API
**Deployment:** Azure Container App

#### H. LLM Classifier Agent ✅ (Existing Logic)
**Source:** `llm_classifier.py`
**Purpose:** AI-based classification and reasoning
**Technology:** Azure OpenAI
**Deployment:** Azure Container App

#### I. Vector Service Agent ✅ (Existing Logic)
**Source:** `embedding_service.py`
**Purpose:** Generate and manage embeddings
**Technology:** Azure OpenAI text-embedding-3-large
**Deployment:** Azure Container App

---

### 4. Shared Data & Services Layer

#### A. Azure Blob Storage (Primary Data Store)
**Purpose:** Persistent storage for all records

**Containers:**
```
gcs-data/
├── evaluations/          # User feedback and evaluations
│   └── YYYY/MM/DD/
│       └── eval-{id}.json
├── submissions/          # All user submissions
│   └── YYYY/MM/DD/
│       └── sub-{id}.json
├── analyses/            # AI analysis results
│   └── YYYY/MM/DD/
│       └── analysis-{id}.json
├── uat-created/         # UAT creation records
│   └── YYYY/MM/DD/
│       └── uat-{id}.json
└── system/              # System configuration
    ├── corrections.json
    ├── retirements.json
    └── issues_actions.json
```

**Why Blob Storage:**
- Container-friendly (no local file dependencies)
- Unlimited retention
- Low cost (~$0.02/GB/month)
- Multi-app access
- Easy backup and migration

#### B. Application Insights (Metrics & Monitoring)
**Purpose:** Real-time metrics, dashboards, and alerting

**What's Tracked:**
- Events: SubmissionReceived, AnalysisCompleted, UATCreated, SearchCompleted
- Metrics: UAT creation rate, search performance, confidence scores
- Dependencies: Azure OpenAI API calls, ADO API calls
- Performance: Response times, error rates
- Custom queries: KQL-based analytics

**Retention:** 90 days default (extendable to 730 days)

#### C. Azure OpenAI (AI Services)
**Resource:** `OpenAI-bp-NorthCentral` (existing)
**Models:**
- `gpt-4o` - Context analysis and reasoning
- `text-embedding-3-large` - Vector embeddings

#### D. Azure DevOps (Work Item System)
**Integration:** REST API 7.0
**Operations:** Create/update/query work items

#### E. Azure Key Vault (Secrets Management)
**Purpose:** Secure storage of credentials
**Contents:**
- Azure OpenAI API keys
- Azure DevOps PAT tokens
- Storage account connection strings
- Service principal credentials

#### F. Azure Container Registry (Image Storage)
**Purpose:** Store Docker images for microservices
**Images:**
- `gcs-context-analyzer:latest`
- `gcs-search-agent:latest`
- `gcs-routing-agent:latest`
- `gcs-user-webapp:latest`
- `gcs-triage-webapp:latest`
- `gcs-api-gateway:latest`

---

## Data Flow Examples

### User Submits Issue

```
1. User Web App → API Gateway
   POST /api/submissions
   { "title": "...", "description": "...", "impact": "..." }

2. API Gateway → Blob Storage
   Store submission: submissions/2026/01/17/sub-abc123.json

3. API Gateway → Context Analyzer Agent
   POST /analyze { "text": "..." }

4. Context Analyzer → Azure OpenAI
   GPT-4o analysis request

5. Context Analyzer → API Gateway
   { "analysis": {...}, "products": [...], "confidence": 0.85 }

6. API Gateway → Application Insights
   Track event: AnalysisCompleted

7. API Gateway → Blob Storage
   Store analysis: analyses/2026/01/17/analysis-abc123.json

8. API Gateway → Search Agent
   POST /search { "query": "...", "products": [...] }

9. Search Agent → Embedding Service
   Generate embeddings

10. Search Agent → Azure DevOps / Vector Search
    Find relevant UATs

11. Search Agent → API Gateway
    { "matches": [...], "total": 15 }

12. API Gateway → User Web App
    Complete results for display
```

### Triage Team Routes UAT

```
1. Triage Web App → API Gateway
   GET /api/submissions?status=unrouted

2. API Gateway → Blob Storage
   Retrieve submissions + analyses

3. Triage Web App displays list

4. User selects UAT to route

5. Triage Web App → API Gateway
   POST /api/route { "uat_id": "...", "override": false }

6. API Gateway → Routing Agent
   { "uat": {...}, "analysis": {...} }

7. Routing Agent → Rules Agent
   Validate routing decision

8. Routing Agent → API Gateway
   { "team": "support", "priority": "high", "assignee": "..." }

9. API Gateway → ADO Integration Agent
   Update work item with routing info

10. API Gateway → Communications Agent
    Notify assigned team member

11. API Gateway → Application Insights
    Track event: UATRouted

12. API Gateway → Blob Storage
    Update routing history
```

---

## Technology Stack

### Current (Existing Code)
- **Language:** Python 3.11+
- **Web Framework:** Flask 3.x
- **AI Services:** Azure OpenAI (GPT-4o, text-embedding-3-large)
- **Vector Search:** FAISS / Custom implementation
- **Integration:** Azure DevOps REST API 7.0
- **Caching:** Local file cache (7-day TTL)
- **Data Storage:** JSON files (local)

### Target (Microservices Architecture)
- **Language:** Python 3.11+
- **API Gateway:** FastAPI or Azure API Management
- **Web Frameworks:** Flask (user app), FastAPI (agents)
- **Frontend:** HTML/Bootstrap → React (future)
- **AI Services:** Azure OpenAI (existing resource)
- **Data Storage:** Azure Blob Storage
- **Metrics:** Application Insights
- **Secrets:** Azure Key Vault
- **Containers:** Docker + Azure Container Apps
- **Container Registry:** Azure Container Registry
- **Orchestration:** Azure Container Apps (managed Kubernetes)
- **CI/CD:** GitHub Actions or Azure DevOps Pipelines

---

## Deployment Model

### Development Environment
- **Resource Group:** `rg-gcs-dev`
- **Region:** North Central US
- **Resources:** All services with `-dev` suffix
- **Cost:** ~$50-100/month

### Production Environment (Future)
- **Resource Group:** `rg-gcs-prod`
- **Region:** North Central US (or multi-region)
- **Resources:** All services with `-prod` suffix
- **Cost:** Scales with usage

### Migration Path
1. Export ARM/Bicep templates from dev
2. Parameterize environment-specific values
3. Deploy to production resource group
4. Update DNS/endpoints
5. Data migration (Blob Storage copy)

---

## Migration to Microsoft 365 Copilot Agents

**Strategy:** Incremental migration, one agent at a time

**Current State:** Microservices in Azure Container Apps

**Future State:** Microsoft 365 Copilot Agents

**Migration Process:**
1. Keep microservice running
2. Wrap agent logic in Bot Framework or Teams AI SDK
3. Create agent manifest (JSON)
4. Deploy to Teams/M365
5. Update API Gateway to route to new endpoint
6. Test in parallel with microservice
7. Cutover when validated
8. Decommission microservice

**Example - Context Analyzer Agent:**

**Before (Microservice):**
```python
# context_analyzer_service.py
@app.post("/analyze")
def analyze(request: AnalysisRequest):
    analyzer = IntelligentContextAnalyzer()
    return analyzer.analyze(request.text)
```

**After (Copilot Agent):**
```python
# context_analyzer_copilot.py
from teams_ai import Application

app = Application()

@app.activity("message")
async def on_message(context: TurnContext):
    analyzer = IntelligentContextAnalyzer()
    result = analyzer.analyze(context.activity.text)
    await context.send_activity(json.dumps(result))
```

**API Gateway Update:**
```python
# Just change endpoint URL
# OLD: http://context-analyzer-svc:8001/analyze
# NEW: https://copilot-context-analyzer.azurewebsites.net/analyze
```

**No web app changes required!**

---

## Why This Architecture?

### Multi-App Support
- API Gateway allows any web app to use the same agents
- User app, triage app, analytics app all share logic
- No code duplication

### Independent Scaling
- Each microservice scales independently
- High-traffic agents (Context Analyzer) can scale out
- Low-traffic agents (Communications) stay small
- Cost-effective

### Technology Flexibility
- Replace individual agents without affecting system
- Migrate to Copilot agents incrementally
- Add new agents (routing, rules) without touching existing code

### Container-Ready
- No local file dependencies (Blob Storage)
- Stateless services (easy to scale)
- Easy deployment (Docker containers)
- Works in any container platform

### Future-Proof
- Clean separation of concerns
- Clear API contracts
- Easy to add new capabilities
- Supports organizational growth

### Development Agility
- Teams can work on agents independently
- Clear interfaces reduce coordination
- Easy testing (mock API Gateway)
- Fast iteration cycles

---

## Next Steps

### Phase 1: Infrastructure Setup ✅ (Current)
- Create Azure resource group `rg-gcs-dev`
- Provision Blob Storage, App Insights, Container Registry
- Setup Key Vault with secrets
- Deploy Container Apps Environment

### Phase 2: Extract First Agents (Week 1-2)
- Create API Gateway scaffold
- Extract Context Analyzer Agent
- Extract Search Agent
- Deploy as containers
- Update user web app to call API Gateway

### Phase 3: Build Triage Web App (Week 2-3)
- Design UI for triage team
- Implement routing interface
- Connect to API Gateway
- Deploy as container

### Phase 4: Add New Agents (Week 3-4)
- Implement Routing Agent
- Implement Rules Agent
- Implement Analytics Agent
- Implement Communications Agent

### Phase 5: Production Readiness (Week 4-5)
- Performance testing
- Security hardening
- Monitoring and alerting
- Documentation
- Production deployment

### Phase 6: Copilot Migration (Future)
- Migrate Context Analyzer to Copilot
- Migrate Search Agent to Copilot
- Continue incremental migration

---

## Documentation Standards

All code and infrastructure will include:

1. **Inline Comments:** Explain complex logic
2. **API Documentation:** OpenAPI/Swagger specs
3. **README Files:** Setup and deployment instructions
4. **Architecture Diagrams:** Visual representations
5. **Runbooks:** Operational procedures
6. **Troubleshooting Guides:** Common issues and solutions

---

## Success Metrics

### User Experience
- Average time to submit issue: < 2 minutes
- Search result relevance: > 80%
- User satisfaction: > 4/5 stars

### Operational Efficiency
- Triage time: < 5 minutes per UAT
- Routing accuracy: > 90%
- SLA compliance: > 95%

### System Performance
- API response time: < 500ms (p95)
- Search response time: < 2 seconds
- System uptime: > 99.5%

### Business Impact
- UAT creation rate: Track monthly
- Time to resolution: Decrease 20%
- Support deflection: 30% reduction in manual triage

---

**Document Version:** 2.0  
**Last Updated:** January 17, 2026  
**Owner:** bprice@microsoft.com  
**Status:** Active Development
