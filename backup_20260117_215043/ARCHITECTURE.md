# GCS Microservices Architecture Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Service Catalog](#service-catalog)
4. [Data Flow Patterns](#data-flow-patterns)
5. [API Contracts](#api-contracts)
6. [Service Dependencies](#service-dependencies)
7. [Technology Stack](#technology-stack)

---

## 🎯 Overview

The Global Customer Success (GCS) system is a distributed microservices architecture consisting of **8 independent services** that provide intelligent UAT management, semantic search, AI-powered analysis, and context evaluation capabilities.

### System Characteristics
- **Architecture Style**: Microservices
- **Communication**: HTTP/REST
- **API Gateway**: Centralized routing and aggregation
- **Total Services**: 8 microservices
- **Deployment Model**: Single-machine development, containerizable for production

### Key Capabilities
- ✅ Intelligent UAT search and management
- ✅ AI-powered text classification and analysis
- ✅ Semantic similarity search with embeddings
- ✅ Context extraction and evaluation
- ✅ Duplicate detection
- ✅ Azure DevOps integration
- ✅ Smart caching with 7-day TTL

---

## 🏗️ Architecture Diagram

```
                          ┌─────────────────────────┐
                          │                         │
                          │     API GATEWAY         │
                          │       Port 8000         │
                          │  - FastAPI              │
                          │  - Route aggregation    │
                          │  - Error handling       │
                          └────────────┬────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
        ┌───────▼───────┐      ┌──────▼──────┐      ┌───────▼───────┐
        │   CONTEXT     │      │   SEARCH    │      │   ENHANCED    │
        │   ANALYZER    │      │   SERVICE   │      │   MATCHING    │
        │   Port 8001   │      │  Port 8002  │      │   Port 8003   │
        │               │      │             │      │               │
        │ - AI analysis │      │ - UAT       │      │ - Completeness│
        │ - Azure svcs  │      │   search    │      │ - Context eval│
        │ - MS products │      │ - Filtering │      │ - Multi-source│
        │ - Tech detect │      │ - Ranking   │      │ - ADO integr  │
        └───────────────┘      └─────────────┘      └───────────────┘
                │                      │                      │
        ┌───────▼───────┐      ┌──────▼──────┐      ┌───────▼───────┐
        │      UAT      │      │     LLM     │      │   EMBEDDING   │
        │  MANAGEMENT   │      │  CLASSIFIER │      │    SERVICE    │
        │   Port 8004   │      │  Port 8005  │      │   Port 8006   │
        │               │      │             │      │               │
        │ - CRUD ops    │      │ - GPT-4     │      │ - text-embed  │
        │ - Lifecycle   │      │ - 20 categ  │      │   3-large     │
        │ - Status      │      │ - Caching   │      │ - 3072 dims   │
        │ - Export      │      │ - Patterns  │      │ - Similarity  │
        └───────────────┘      └─────────────┘      └───────┬───────┘
                                                             │
                                                     ┌───────▼───────┐
                                                     │    VECTOR     │
                                                     │    SEARCH     │
                                                     │   Port 8007   │
                                                     │               │
                                                     │ - Cosine sim  │
                                                     │ - Collections │
                                                     │ - Duplicate   │
                                                     │   detection   │
                                                     └───────────────┘

                          ┌─────────────────────────┐
                          │    SHARED LIBRARIES     │
                          │  (in each service)      │
                          │                         │
                          │  - cache_manager.py     │
                          │  - ai_config.py         │
                          └─────────────────────────┘

                          ┌─────────────────────────┐
                          │   EXTERNAL SERVICES     │
                          │                         │
                          │  - Azure OpenAI         │
                          │  - Azure DevOps         │
                          │  - Application Insights │
                          └─────────────────────────┘
```

---

## 🎯 Service Catalog

### 1. API Gateway (Port 8000)
**Purpose**: Central entry point for all client requests

**Responsibilities**:
- Route requests to appropriate microservices
- Request/response aggregation
- Error handling and standardization
- CORS management
- Health check aggregation

**Technology**: FastAPI + uvicorn

**Routes**:
- `/api/search/*` → Search Service (8002)
- `/api/analyze/*` → Context Analyzer (8001)
- `/api/uat/*` → UAT Management (8004)
- `/api/context/*` → Context Analyzer (8001)
- `/api/matching/*` → Enhanced Matching (8003)
- `/api/classify/*` → LLM Classifier (8005)
- `/api/embedding/*` → Embedding Service (8006)
- `/api/vector/*` → Vector Search (8007)

**Key Features**:
- Centralized error handling
- Service health monitoring
- API documentation (Swagger UI)
- Configurable timeouts per endpoint

---

### 2. Context Analyzer (Port 8001)
**Purpose**: Extract and analyze contextual information from text

**Responsibilities**:
- Detect Microsoft products (12 products)
- Identify Azure services (200+ services)
- Extract technologies (50+ tech)
- Determine Azure regions
- Analyze regional service availability
- Smart caching of analysis results

**Technology**: FastAPI + Azure OpenAI GPT-4

**Key Endpoints**:
- `POST /analyze` - Comprehensive context analysis
- `POST /analyze/batch` - Batch processing
- `GET /health` - Health check
- `GET /info` - Service information

**Analysis Output**:
```json
{
  "microsoft_products": ["Azure", "Office 365"],
  "azure_services": ["Azure AD", "Azure SQL"],
  "technologies": ["SSO", "REST API"],
  "azure_regions": ["East US", "West Europe"],
  "regional_availability": {...},
  "analysis_metadata": {...}
}
```

**Cache Strategy**: File-based with 7-day TTL

---

### 3. Search Service (Port 8002)
**Purpose**: Search and retrieve UATs from the knowledge base

**Responsibilities**:
- Full-text UAT search
- Filtering by status, priority, category
- Result ranking and scoring
- Pagination support
- Search history tracking

**Technology**: FastAPI + Python search algorithms

**Key Endpoints**:
- `POST /search` - Search UATs
- `GET /uats` - List all UATs
- `GET /uats/{id}` - Get specific UAT
- `GET /categories` - List categories
- `GET /health` - Health check

**Search Features**:
- Multi-field search (title, description, steps)
- Fuzzy matching
- Relevance scoring
- Status-based filtering
- Priority-based sorting

---

### 4. Enhanced Matching (Port 8003)
**Purpose**: Intelligent UAT matching and analysis

**Responsibilities**:
- Completeness analysis (AI-powered)
- Context evaluation for UATs
- Multi-source intelligent search
- Azure DevOps integration (UAT + TFT)
- Confidence scoring

**Technology**: FastAPI + Azure OpenAI GPT-4

**Key Endpoints**:
- `POST /analyze/completeness` - Analyze UAT completeness
- `POST /analyze/context` - Context-based evaluation
- `POST /search/intelligent` - Multi-source search
- `GET /health` - Health check

**Completeness Analysis Output**:
```json
{
  "completeness_score": 0.85,
  "has_clear_objective": true,
  "has_test_steps": true,
  "has_expected_results": true,
  "missing_elements": ["preconditions"],
  "suggestions": ["Add preconditions section"],
  "confidence": 0.92
}
```

**Integration**:
- Azure DevOps API for UAT retrieval
- Technical Feedback Team (TFT) data

---

### 5. UAT Management (Port 8004)
**Purpose**: CRUD operations for UAT lifecycle management

**Responsibilities**:
- Create, read, update, delete UATs
- Status management (draft, in_progress, completed)
- Priority assignment
- UAT export (JSON, CSV)
- Bulk operations

**Technology**: FastAPI + JSON file storage

**Key Endpoints**:
- `POST /uats` - Create UAT
- `GET /uats` - List all UATs
- `GET /uats/{id}` - Get UAT by ID
- `PUT /uats/{id}` - Update UAT
- `DELETE /uats/{id}` - Delete UAT
- `GET /export` - Export UATs
- `GET /health` - Health check

**UAT Schema**:
```json
{
  "id": "uat-001",
  "title": "Test Title",
  "description": "Test Description",
  "status": "in_progress",
  "priority": "high",
  "created_at": "2026-01-17T10:00:00",
  "updated_at": "2026-01-17T12:00:00",
  "tags": ["authentication", "security"]
}
```

---

### 6. LLM Classifier (Port 8005)
**Purpose**: AI-powered text classification using GPT-4

**Responsibilities**:
- Classify text into 20 categories
- Determine intent (15 intent types)
- Assess business impact (4 levels)
- Pattern matching integration
- Confidence scoring
- Smart caching with 7-day TTL

**Technology**: FastAPI + Azure OpenAI GPT-4

**Key Endpoints**:
- `POST /classify` - Classify single text
- `POST /classify/batch` - Batch classification
- `GET /categories` - List all categories
- `GET /intents` - List all intents
- `GET /cache/stats` - Cache statistics
- `GET /health` - Health check

**Categories** (20):
- Technical Support, Feature Request, Bug Report, Performance Issue
- Security Concern, Integration Question, Configuration Help
- Documentation Request, Training Request, Feedback
- Compliance Question, Billing Question, Account Management
- Service Outage, Best Practices, Architecture Guidance
- Migration Help, Roadmap Inquiry, General Question, Other

**Intents** (15):
- seeking_help, requesting_feature, reporting_issue, seeking_guidance
- requesting_information, providing_feedback, requesting_clarification
- expressing_concern, requesting_change, requesting_documentation
- requesting_access, escalating_issue, requesting_update
- asking_question, other

**Business Impact** (4 levels):
- critical, high, medium, low

**Classification Output**:
```json
{
  "category": "Technical Support",
  "intent": "seeking_help",
  "business_impact": "high",
  "confidence": 0.92,
  "reasoning": "User needs immediate assistance...",
  "suggested_action": "Escalate to support team",
  "cache_hit": false
}
```

---

### 7. Embedding Service (Port 8006)
**Purpose**: Generate text embeddings using Azure OpenAI

**Responsibilities**:
- Single text embedding generation
- Batch embedding processing
- Context embedding (title + description + impact)
- Cosine similarity calculation
- Cache management
- Smart caching with 7-day TTL

**Technology**: FastAPI + Azure OpenAI text-embedding-3-large

**Key Endpoints**:
- `POST /embed` - Single text embedding
- `POST /embed/batch` - Batch embeddings
- `POST /embed/context` - Context embedding
- `POST /similarity` - Calculate similarity
- `GET /cache/stats` - Cache statistics
- `DELETE /cache/clear` - Clear cache
- `GET /health` - Health check

**Embedding Model**:
- Model: text-embedding-3-large
- Dimensions: 3072
- Max tokens: 8191

**Embedding Output**:
```json
{
  "embedding": [0.0123, -0.0456, ...],  // 3072 floats
  "dimension": 3072,
  "model": "text-embedding-3-large",
  "cache_hit": false
}
```

**Similarity Calculation**:
- Algorithm: Cosine similarity
- Range: -1.0 to 1.0 (typically 0.0 to 1.0)
- Threshold: Configurable per use case

---

### 8. Vector Search (Port 8007)
**Purpose**: Semantic similarity search using vector embeddings

**Responsibilities**:
- Index items with embeddings
- Semantic similarity search
- Context-based search (title + description)
- Duplicate detection (0.70 threshold)
- Multi-collection management
- In-memory vector index

**Technology**: FastAPI + sklearn cosine_similarity

**Key Endpoints**:
- `POST /index` - Index items into collection
- `POST /search` - Semantic similarity search
- `POST /search/context` - Context-based search
- `POST /search/similar` - Find similar items (duplicate detection)
- `GET /collections` - List all collections
- `GET /collections/{name}/stats` - Collection statistics
- `DELETE /collections/{name}` - Clear collection
- `POST /collections/clear-all` - Clear all collections
- `GET /health` - Health check

**Search Algorithm**:
1. Generate embedding for query (via Embedding Service)
2. Calculate cosine similarity with all items in collection
3. Filter by similarity threshold (default: 0.75)
4. Sort by similarity (descending)
5. Return top-K results (default: 10)

**Collection Structure**:
```json
{
  "collection_name": "uats",
  "items": [
    {
      "id": "uat-001",
      "title": "Test Title",
      "description": "Test Description",
      "embedding": [0.0123, ...],  // 3072 floats
      "metadata": {"priority": "high"}
    }
  ]
}
```

**Duplicate Detection**:
- Higher threshold: 0.70
- Searches multiple collections
- Returns items above threshold
- Use case: Prevent duplicate UAT creation

---

## 🔄 Data Flow Patterns

### Pattern 1: Intelligent UAT Search
```
User Query
    ↓
API Gateway (8000)
    ↓
Context Analyzer (8001) ─────→ Extract context
    ↓
LLM Classifier (8005) ────────→ Classify intent
    ↓
Search Service (8002) ─────────→ Find UATs
    ↓
Enhanced Matching (8003) ─────→ Analyze completeness
    ↓
API Gateway (8000)
    ↓
Response to User
```

### Pattern 2: Semantic Search
```
User Query
    ↓
API Gateway (8000)
    ↓
Embedding Service (8006) ─────→ Generate query embedding
    ↓
Vector Search (8007) ──────────→ Cosine similarity search
    ↓
API Gateway (8000)
    ↓
Response with ranked results
```

### Pattern 3: UAT Creation with Duplicate Detection
```
New UAT Data
    ↓
API Gateway (8000)
    ↓
Vector Search (8007) ──────────→ Check for duplicates
    ↓
(If no duplicates)
    ↓
UAT Management (8004) ─────────→ Create UAT
    ↓
Context Analyzer (8001) ───────→ Analyze context
    ↓
LLM Classifier (8005) ─────────→ Classify category
    ↓
Vector Search (8007) ──────────→ Index for future searches
    ↓
Response with UAT ID
```

### Pattern 4: Batch Processing
```
Multiple Items
    ↓
API Gateway (8000)
    ↓
LLM Classifier (8005) ─────────→ Classify all items
    │                             (single API call to GPT-4)
    ↓
Embedding Service (8006) ──────→ Generate all embeddings
    │                             (batch API call)
    ↓
Vector Search (8007) ──────────→ Index all items
    ↓
Response with results
```

---

## 📡 API Contracts

### Standard Response Format

**Success Response**:
```json
{
  "status": "success",
  "data": {...},
  "metadata": {
    "timestamp": "2026-01-17T10:00:00Z",
    "service": "context-analyzer",
    "request_id": "abc123"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Query text is required",
    "details": {...}
  },
  "metadata": {
    "timestamp": "2026-01-17T10:00:00Z",
    "service": "search-service"
  }
}
```

### Health Check Contract
All services implement:
```
GET /health

Response:
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0",
  "uptime": 3600,
  "dependencies": {
    "azure_openai": "connected",
    "cache": "available"
  }
}
```

### Service Info Contract
All services implement:
```
GET /info

Response:
{
  "name": "Service Name",
  "version": "1.0.0",
  "description": "Service description",
  "endpoints": [...],
  "capabilities": [...],
  "dependencies": [...]
}
```

---

## 🔗 Service Dependencies

### Dependency Graph
```
API Gateway (8000)
  ├─→ Context Analyzer (8001)
  │     └─→ Azure OpenAI (GPT-4)
  ├─→ Search Service (8002)
  │     └─→ [No external dependencies]
  ├─→ Enhanced Matching (8003)
  │     ├─→ Azure OpenAI (GPT-4)
  │     └─→ Azure DevOps API
  ├─→ UAT Management (8004)
  │     └─→ [No external dependencies]
  ├─→ LLM Classifier (8005)
  │     └─→ Azure OpenAI (GPT-4)
  ├─→ Embedding Service (8006)
  │     └─→ Azure OpenAI (text-embedding-3-large)
  └─→ Vector Search (8007)
        └─→ Embedding Service (8006)

All Services:
  └─→ Application Insights (optional)
```

### Critical Dependencies
- **Azure OpenAI**: 5 services depend on it (Context, Matching, Classifier, Embedding, Vector via Embedding)
- **Embedding Service**: Vector Search requires it for embedding generation
- **Cache Manager**: Used by Classifier, Embedding, and other services (shared library)

### Failure Modes
- **Azure OpenAI down**: Services return cached results or fail gracefully
- **Embedding Service down**: Vector Search cannot perform new searches (cached results still work)
- **API Gateway down**: All services still accessible directly by port
- **Individual service down**: Other services unaffected (loose coupling)

---

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI**: All 8 services
- **uvicorn**: ASGI server
- **Python**: 3.11+

### AI/ML Services
- **Azure OpenAI**:
  - GPT-4 (gpt-4-32k) for classification and analysis
  - text-embedding-3-large for embeddings
- **scikit-learn**: Cosine similarity calculations
- **numpy**: Vector operations

### Data Storage
- **File-based JSON**: UAT storage, cache storage
- **In-memory**: Vector Search collections
- **Future**: Redis, PostgreSQL with pgvector

### Observability
- **Application Insights**: Azure monitoring (optional)
- **Logging**: Python logging module
- **Health Checks**: Built into all services

### Development Tools
- **Git**: Version control
- **PowerShell**: Deployment scripts
- **pytest**: Testing framework (test files created)

### Communication
- **HTTP/REST**: Inter-service communication
- **JSON**: Data serialization
- **httpx**: Async HTTP client

---

## 📊 Performance Characteristics

### Response Times (Typical)
- **API Gateway**: <10ms (routing only)
- **Context Analyzer**: 1-3s (GPT-4 API call)
- **Search Service**: 50-200ms (in-memory search)
- **Enhanced Matching**: 2-4s (GPT-4 API call)
- **UAT Management**: 10-50ms (file I/O)
- **LLM Classifier**: 1-3s (GPT-4 API call, <10ms if cached)
- **Embedding Service**: 1-2s (Embedding API call, <10ms if cached)
- **Vector Search**: 1-2s (embedding generation + <100ms similarity calc)

### Cache Hit Rates (After Warm-up)
- **LLM Classifier**: 70-80%
- **Embedding Service**: 60-70%
- **Context Analyzer**: 50-60%

### Scalability Limits (Current)
- **Vector Search**: ~1M items in-memory (12-15GB RAM)
- **Search Service**: ~100K UATs (file-based)
- **Concurrent Requests**: Limited by Azure OpenAI rate limits
- **Cache Size**: Unlimited (file-based, limited by disk)

### Bottlenecks
1. **Azure OpenAI API calls**: 1-3s latency
2. **File I/O**: For large UAT collections
3. **Vector Search indexing**: O(n) per item for embedding generation

---

## 🔐 Security Considerations

### Authentication
- **Azure AD**: For Azure OpenAI API
- **Personal Access Tokens**: For Azure DevOps API
- **No user authentication**: Currently (development phase)

### Authorization
- **Service-to-service**: No auth (trusted network)
- **External APIs**: Credential-based

### Data Protection
- **Sensitive data**: Not logged
- **Cache encryption**: Not implemented (file permissions only)
- **HTTPS**: Not enforced (development phase)

### Future Improvements
- [ ] API key authentication for gateway
- [ ] OAuth 2.0 for user authentication
- [ ] Request rate limiting
- [ ] Encrypted cache storage
- [ ] HTTPS everywhere

---

## 📈 Future Enhancements

### Short-term (1-3 months)
- [ ] Replace file storage with PostgreSQL
- [ ] Add Redis for distributed caching
- [ ] Implement API Gateway rate limiting
- [ ] Add request tracing (correlation IDs)
- [ ] Containerize all services with Docker

### Medium-term (3-6 months)
- [ ] Migrate Vector Search to FAISS
- [ ] Add Kubernetes orchestration
- [ ] Implement circuit breakers
- [ ] Add message queue (RabbitMQ/Kafka)
- [ ] Real-time monitoring dashboard

### Long-term (6-12 months)
- [ ] Service mesh (Istio)
- [ ] GraphQL gateway option
- [ ] Multi-region deployment
- [ ] Advanced analytics and ML models
- [ ] Self-healing capabilities

---

## 📚 Additional Resources

- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Phase Summaries**: `PHASE_*_SUMMARY.md` files
- **Test Suites**: `test_phase_*.py` and `test_end_to_end.py`

---

**Last Updated**: January 17, 2026  
**Architecture Version**: 1.0  
**Total Services**: 8 microservices  
**Status**: Production-ready (development environment)
