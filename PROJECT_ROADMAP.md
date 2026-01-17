# GCS Project Implementation Roadmap
**Version:** 1.0  
**Date:** January 17, 2026  
**Status:** Active Planning

---

## Overview

This roadmap outlines the step-by-step transformation of the current monolithic Flask application into a microservices-based architecture supporting multiple web applications and eventual Microsoft 365 Copilot integration.

---

## Project Structure (Target State)

```
GCS/
├── docs/                              # All documentation
│   ├── GCS_ARCHITECTURE.md            # ✅ High-level architecture
│   ├── INFRASTRUCTURE_PLAN.md         # ✅ Azure infrastructure details
│   ├── API_CONTRACTS.md               # API specifications
│   ├── DEPLOYMENT_GUIDE.md            # Deployment procedures
│   └── TROUBLESHOOTING.md             # Common issues
│
├── infrastructure/                    # Infrastructure as Code
│   ├── bicep/                         # Bicep templates
│   │   ├── main.bicep                 # Main deployment
│   │   ├── storage.bicep              # Storage resources
│   │   ├── containers.bicep           # Container Apps
│   │   └── monitoring.bicep           # App Insights, Log Analytics
│   ├── terraform/                     # Alternative: Terraform (optional)
│   └── scripts/                       # Deployment scripts
│       ├── deploy-infrastructure.sh
│       ├── migrate-data.py
│       └── setup-secrets.sh
│
├── api-gateway/                       # Central API Gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                        # FastAPI application
│   ├── routers/                       # API route handlers
│   │   ├── __init__.py
│   │   ├── analysis.py                # /api/analyze routes
│   │   ├── search.py                  # /api/search routes
│   │   ├── routing.py                 # /api/route routes
│   │   ├── evaluations.py             # /api/evaluations routes
│   │   └── metrics.py                 # /api/metrics routes
│   ├── services/                      # Service clients
│   │   ├── __init__.py
│   │   ├── agent_client.py            # Generic agent HTTP client
│   │   ├── storage_client.py          # Blob Storage access
│   │   └── insights_client.py         # App Insights logging
│   ├── models/                        # Pydantic data models
│   │   ├── __init__.py
│   │   ├── requests.py                # Request schemas
│   │   └── responses.py               # Response schemas
│   ├── config.py                      # Configuration from Key Vault
│   └── tests/                         # Unit tests
│
├── agents/                            # Microservices (Agents)
│   │
│   ├── context-analyzer/              # Context Analyzer Agent
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py                    # FastAPI service
│   │   ├── analyzer.py                # Core logic (from intelligent_context_analyzer.py)
│   │   ├── config.py
│   │   └── tests/
│   │
│   ├── search-agent/                  # Search Agent
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── search_service.py          # From search_service.py
│   │   ├── vector_search.py           # From vector_search.py
│   │   ├── hybrid_analyzer.py         # From hybrid_context_analyzer.py
│   │   └── tests/
│   │
│   ├── routing-agent/                 # Routing Agent (NEW)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── router.py                  # Routing logic
│   │   ├── rules.py                   # Routing rules
│   │   └── tests/
│   │
│   ├── rules-agent/                   # Rules Engine Agent (NEW)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── engine.py                  # Rules engine
│   │   ├── validators.py              # Validation logic
│   │   └── tests/
│   │
│   ├── analytics-agent/               # Analytics Agent (NEW)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── metrics.py                 # Metrics calculation
│   │   ├── reports.py                 # Report generation
│   │   └── tests/
│   │
│   ├── comms-agent/                   # Communications Agent (NEW)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── notifier.py                # Notification logic
│   │   ├── templates/                 # Email/message templates
│   │   └── tests/
│   │
│   ├── ado-integration/               # ADO Integration Agent
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── ado_client.py              # From ado_integration.py
│   │   └── tests/
│   │
│   ├── llm-classifier/                # LLM Classifier Agent
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── main.py
│   │   ├── classifier.py              # From llm_classifier.py
│   │   └── tests/
│   │
│   └── vector-service/                # Vector/Embedding Service
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── main.py
│       ├── embedding_service.py       # From embedding_service.py
│       └── tests/
│
├── webapps/                           # Web Applications
│   │
│   ├── user-submission/               # User Submission App (refactored)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py                     # Flask app (routes only)
│   │   ├── config.py
│   │   ├── services/
│   │   │   └── api_client.py          # Calls API Gateway
│   │   ├── templates/                 # HTML templates
│   │   ├── static/                    # CSS, JS, images
│   │   └── tests/
│   │
│   └── triage-management/             # Triage Management App (NEW)
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app.py                     # Flask/React app
│       ├── config.py
│       ├── services/
│       │   └── api_client.py          # Calls API Gateway
│       ├── frontend/                  # React app (if using React)
│       │   ├── package.json
│       │   ├── src/
│       │   └── public/
│       ├── templates/                 # Flask templates (if not using React)
│       ├── static/
│       └── tests/
│
├── shared/                            # Shared libraries
│   ├── __init__.py
│   ├── models.py                      # Common data models
│   ├── config.py                      # Shared configuration
│   ├── auth.py                        # Authentication helpers
│   └── utils.py                       # Utility functions
│
├── tests/                             # Integration tests
│   ├── integration/
│   ├── e2e/
│   └── performance/
│
├── scripts/                           # Utility scripts
│   ├── migrate-data.py                # Migrate JSON to Blob Storage
│   ├── generate-api-keys.py
│   └── health-check.py
│
├── .github/                           # GitHub Actions CI/CD
│   └── workflows/
│       ├── build-agents.yml
│       ├── build-webapps.yml
│       ├── deploy-dev.yml
│       └── deploy-prod.yml
│
├── docker-compose.yml                 # Local development environment
├── .env.example                       # Example environment variables
├── .gitignore
├── README.md                          # Project overview
└── CHANGELOG.md                       # Version history
```

---

## Implementation Phases

### ✅ Phase 0: Planning & Documentation (Current)
**Duration:** 1 day  
**Status:** In Progress

**Tasks:**
- [x] Create `GCS_ARCHITECTURE.md`
- [x] Create `INFRASTRUCTURE_PLAN.md`
- [x] Create `PROJECT_ROADMAP.md` (this file)
- [ ] Review and approve architecture
- [ ] Identify any gaps or risks

**Deliverables:**
- Complete architecture documentation
- Infrastructure deployment plan
- Implementation roadmap

---

### Phase 1: Infrastructure Setup
**Duration:** 2-3 days  
**Status:** Not Started  
**Prerequisites:** Phase 0 complete

**Tasks:**
1. [ ] Create Azure resource group `rg-gcs-dev`
2. [ ] Provision Storage Account `stgcsdev001`
3. [ ] Create Blob container `gcs-data` with subdirectories
4. [ ] Provision Application Insights `appi-gcs-dev`
5. [ ] Create Container Registry `acrgcsdev001`
6. [ ] Provision Container Apps Environment `cae-gcs-dev`
7. [ ] Create Key Vault `kv-gcs-dev-001`
8. [ ] Store all secrets in Key Vault
9. [ ] Setup managed identities and RBAC
10. [ ] Verify connectivity between all services

**Deliverables:**
- All Azure resources provisioned
- Secrets stored securely
- Infrastructure documentation updated

**Validation:**
- Storage account accessible
- App Insights receiving test telemetry
- Container Apps Environment ready
- Key Vault secrets retrievable

---

### Phase 2: Data Migration
**Duration:** 1 day  
**Status:** Not Started  
**Prerequisites:** Phase 1 complete

**Tasks:**
1. [ ] Create data migration script `scripts/migrate-data.py`
2. [ ] Migrate `context_evaluations.json` to Blob Storage
3. [ ] Migrate `corrections.json` to Blob Storage
4. [ ] Migrate `retirements.json` to Blob Storage
5. [ ] Migrate `issues_actions.json` to Blob Storage
6. [ ] Verify data integrity
7. [ ] Create backup of original files
8. [ ] Document migration process

**Deliverables:**
- All data in Blob Storage
- Migration script for future use
- Data validation report

**Validation:**
- All JSON files accessible from Blob Storage
- Data structure preserved
- Performance acceptable (< 500ms reads)

---

### Phase 3: API Gateway Development
**Duration:** 3-4 days  
**Status:** Not Started  
**Prerequisites:** Phase 1 complete

**Tasks:**
1. [ ] Create `api-gateway/` directory structure
2. [ ] Setup FastAPI application
3. [ ] Implement configuration from Key Vault
4. [ ] Create API route stubs (analyze, search, route, etc.)
5. [ ] Implement storage client (Blob Storage access)
6. [ ] Implement App Insights logging
7. [ ] Create API documentation (OpenAPI/Swagger)
8. [ ] Write unit tests
9. [ ] Create Dockerfile
10. [ ] Test locally with docker-compose

**Deliverables:**
- Functional API Gateway (stub responses)
- Swagger documentation at `/docs`
- Docker image built and tested
- Unit tests passing

**Validation:**
- API Gateway responds to health checks
- Can access Blob Storage
- Can log to App Insights
- Documentation accessible

---

### Phase 4: Extract Context Analyzer Agent
**Duration:** 3-4 days  
**Status:** Not Started  
**Prerequisites:** Phase 3 complete

**Tasks:**
1. [ ] Create `agents/context-analyzer/` directory
2. [ ] Copy `intelligent_context_analyzer.py` logic
3. [ ] Create FastAPI service wrapper
4. [ ] Implement `/analyze` endpoint
5. [ ] Add configuration from Key Vault
6. [ ] Add App Insights telemetry
7. [ ] Write unit tests
8. [ ] Create Dockerfile
9. [ ] Deploy to Container Apps
10. [ ] Update API Gateway to call agent
11. [ ] Integration testing

**Deliverables:**
- Context Analyzer agent deployed
- API Gateway integration working
- Agent accessible at `https://ca-context-analyzer-dev.northcentralus.azurecontainerapps.io`
- Tests passing

**Validation:**
- Agent responds to analysis requests
- Results match current implementation
- Performance acceptable (< 2s per analysis)
- Telemetry flowing to App Insights

---

### Phase 5: Extract Search Agent
**Duration:** 3-4 days  
**Status:** Not Started  
**Prerequisites:** Phase 4 complete

**Tasks:**
1. [ ] Create `agents/search-agent/` directory
2. [ ] Copy search_service.py, vector_search.py, hybrid_context_analyzer.py
3. [ ] Create FastAPI service wrapper
4. [ ] Implement `/search` endpoint
5. [ ] Add configuration from Key Vault
6. [ ] Add App Insights telemetry
7. [ ] Write unit tests
8. [ ] Create Dockerfile
9. [ ] Deploy to Container Apps
10. [ ] Update API Gateway to call agent
11. [ ] Integration testing

**Deliverables:**
- Search Agent deployed
- API Gateway integration working
- Tests passing

**Validation:**
- Agent performs vector search correctly
- ADO integration working
- Search results match current implementation

---

### Phase 6: Extract Supporting Agents
**Duration:** 2-3 days  
**Status:** Not Started  
**Prerequisites:** Phase 5 complete

**Tasks:**
1. [ ] Extract ADO Integration Agent
2. [ ] Extract LLM Classifier Agent
3. [ ] Extract Vector Service Agent
4. [ ] Deploy all to Container Apps
5. [ ] Update API Gateway integrations
6. [ ] Integration testing

**Deliverables:**
- All existing agents deployed
- API Gateway fully integrated
- Tests passing

---

### Phase 7: Refactor User Web App
**Duration:** 3-4 days  
**Status:** Not Started  
**Prerequisites:** Phases 4-6 complete

**Tasks:**
1. [ ] Create `webapps/user-submission/` directory
2. [ ] Extract Flask routes from current `app.py`
3. [ ] Remove all business logic (now in agents)
4. [ ] Create API client to call API Gateway
5. [ ] Update templates to use new data flow
6. [ ] Add configuration from Key Vault
7. [ ] Write tests
8. [ ] Create Dockerfile
9. [ ] Deploy to Container Apps
10. [ ] Full end-to-end testing

**Deliverables:**
- User web app refactored and deployed
- All features working (wizard, search, UAT creation)
- Tests passing

**Validation:**
- User can submit issues
- AI analysis works
- Search works
- UAT creation works
- No regressions from current system

---

### Phase 8: Build New Agents
**Duration:** 5-7 days  
**Status:** Not Started  
**Prerequisites:** Phase 7 complete

**Tasks:**
1. [ ] Build Routing Agent (team assignment, priority)
2. [ ] Build Rules Agent (validation, policies)
3. [ ] Build Analytics Agent (metrics, reports)
4. [ ] Build Communications Agent (notifications)
5. [ ] Deploy all to Container Apps
6. [ ] Update API Gateway
7. [ ] Integration testing

**Deliverables:**
- 4 new agents deployed and functional
- API Gateway routes configured
- Documentation complete

**Validation:**
- Routing agent assigns teams correctly
- Rules agent validates requests
- Analytics agent generates metrics
- Comms agent sends notifications

---

### Phase 9: Build Triage Web App
**Duration:** 5-7 days  
**Status:** Not Started  
**Prerequisites:** Phase 8 complete

**Tasks:**
1. [ ] Design UI/UX for triage team
2. [ ] Create `webapps/triage-management/` directory
3. [ ] Build Flask/React application
4. [ ] Implement triage dashboard
5. [ ] Implement routing interface
6. [ ] Implement analytics views
7. [ ] Create API client to call API Gateway
8. [ ] Write tests
9. [ ] Create Dockerfile
10. [ ] Deploy to Container Apps
11. [ ] User acceptance testing

**Deliverables:**
- Triage web app deployed
- Triage team can view and route UATs
- Analytics visible
- Tests passing

**Validation:**
- Triage team can access all UATs
- Can see original AI analysis
- Can route to teams
- Can override recommendations
- Performance acceptable

---

### Phase 10: Production Readiness
**Duration:** 5-7 days  
**Status:** Not Started  
**Prerequisites:** Phase 9 complete

**Tasks:**
1. [ ] Performance testing
2. [ ] Load testing
3. [ ] Security audit
4. [ ] Setup production monitoring
5. [ ] Create alerting rules
6. [ ] Write operational runbooks
7. [ ] Create disaster recovery plan
8. [ ] Document troubleshooting procedures
9. [ ] Setup CI/CD pipelines
10. [ ] Create production infrastructure
11. [ ] Deploy to production
12. [ ] Production smoke testing

**Deliverables:**
- System production-ready
- Monitoring and alerting configured
- Documentation complete
- Production deployed

**Validation:**
- System handles production load
- Security requirements met
- Monitoring working
- Alerts firing correctly

---

### Phase 11: Copilot Migration (Future)
**Duration:** 3-4 weeks  
**Status:** Future  
**Prerequisites:** Phase 10 complete, stable production

**Tasks:**
1. [ ] Research Microsoft 365 Copilot agent requirements
2. [ ] Create agent manifests
3. [ ] Migrate Context Analyzer to Copilot (pilot)
4. [ ] Test in parallel with microservice
5. [ ] Update API Gateway routing
6. [ ] Cutover Context Analyzer
7. [ ] Migrate remaining agents one-by-one
8. [ ] Decommission microservices
9. [ ] Update documentation

**Deliverables:**
- All agents running as Copilot agents
- API Gateway updated
- Microservices decommissioned

---

## Risk Management

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API Gateway becomes bottleneck | High | Medium | Design for scalability, load testing early |
| Agent communication latency | Medium | Medium | Optimize network, use caching |
| Data migration issues | High | Low | Test thoroughly, keep backups |
| Container Apps learning curve | Medium | Medium | Start simple, iterate |
| Cost overruns | Medium | Low | Monitor costs weekly, set alerts |

### Schedule Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Clear phase gates, approve changes formally |
| Dependencies block progress | Medium | Parallel workstreams where possible |
| Resource availability | Medium | Document everything for handoff |
| Testing takes longer | Medium | Allocate 20% buffer in each phase |

---

## Success Criteria

### Phase Completion
- All tasks complete
- Tests passing
- Documentation updated
- Validation criteria met
- Demo successful

### Project Completion
- All phases complete
- Production deployed
- User acceptance passed
- Performance targets met
- Documentation complete

---

## Current Status Summary

**Phase 0:** ✅ In Progress  
**Phase 1:** ⏸️ Awaiting approval  
**Phase 2-11:** ⏸️ Not started

**Next Action:** Create Azure resource group and begin infrastructure provisioning

---

**Document Version:** 1.0  
**Last Updated:** January 17, 2026  
**Owner:** bprice@microsoft.com
