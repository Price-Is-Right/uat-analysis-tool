# System Architecture Documentation

## Overview

This is an intelligent issue tracking and matching system that uses hybrid AI (LLM + pattern matching) to analyze, classify, and route support issues to Azure DevOps work items and retirement documentation.

## System Components

### 1. Hybrid Context Analyzer (`hybrid_context_analyzer.py`)

**Purpose**: Primary analysis engine combining AI and pattern matching

**Architecture**:
```
User Input → Pattern Analysis → AI Enhancement → Similarity Search → Final Result
              ↓                    ↓                 ↓
          (baseline)         (intelligent)      (historical)
```

**Key Features**:
- **Pattern-First Strategy**: Always runs fast rule-based analysis first
- **AI Enhancement**: GPT-4 provides semantic understanding and reasoning
- **Graceful Fallback**: Falls back to patterns if AI unavailable
- **Corrective Learning**: Learns from user feedback (Phase 1 implemented)
- **Vector Search**: Finds semantically similar historical issues

**Result Structure**:
```python
HybridAnalysisResult(
    # Primary classification
    category="technical_support",
    intent="seeking_guidance",
    confidence=0.95,
    business_impact="high",
    reasoning="User needs help configuring...",
    
    # Pattern evidence
    pattern_category="technical_support",
    pattern_confidence=0.75,
    pattern_features={...},
    
    # Semantic data
    semantic_keywords=["azure", "configuration", ...],
    key_concepts=["networking", "security", ...],
    domain_entities={"services": ["Azure VPN"], ...},
    
    # Routing info
    recommended_search_strategy={
        "search_retirements": False,
        "prioritize_uats": True,
        ...
    },
    urgency_level="medium",
    technical_complexity="low",
    
    # Metadata
    source="hybrid",  # "llm", "pattern", or "hybrid"
    agreement=True
)
```

### 2. Pattern Context Analyzer (`intelligent_context_analyzer.py`)

**Purpose**: Fast, rule-based analysis with comprehensive domain knowledge

**Features**:
- **10-Step Analysis Process**: Systematic classification pipeline
- **Microsoft Product Detection**: Recognizes 100+ Azure services
- **Domain Entity Extraction**: Identifies services, frameworks, regions
- **Confidence Scoring**: 0.50-1.0 range based on evidence strength
- **Search Strategy Recommendation**: Routes to appropriate data sources
- **Full Transparency**: Complete step-by-step reasoning

**Categories Supported**:
- Technical Support
- Feature Requests
- Service Availability
- Roadmap Inquiries
- Capacity Issues
- Data Sovereignty
- Service Retirements
- Compliance Inquiries

**Intent Types**:
- Seeking Guidance
- Troubleshooting Issue
- Requesting Feature
- Requesting Service
- Roadmap Inquiry
- Capacity Request
- Escalation Request
- And more...

### 3. Enhanced Matching Engine (`enhanced_matching.py`)

**Purpose**: Multi-source search and intelligent matching

**Data Sources**:
1. **Azure DevOps**: Work items (UATs, features, bugs)
2. **Retirement Database**: Service end-of-life information
3. **Vector Search**: Semantic similarity matching

**Matching Flow**:
```
Issue → Context Analysis → Search Strategy → Multi-Source Search → Scoring → Ranking
         ↓                   ↓                  ↓                    ↓         ↓
    (AI+Pattern)     (which sources?)   (parallel queries)    (relevance)  (best matches)
```

**Intelligent Features**:
- **Context-Aware Search**: Uses analysis to determine which sources to search
- **Semantic Enrichment**: Expands search terms using keywords and concepts
- **Priority Routing**: Routes capacity/retirement issues appropriately
- **Intelligent Compilation**: Combines results from multiple sources
- **Relevance Scoring**: Ranks matches by semantic similarity and metadata

### 4. Flask Web Application (`app.py`)

**Purpose**: Web interface for submission, analysis, and corrections

**Key Routes**:

#### `/quick_ica` (POST)
- Quick submission form (bypasses wizard)
- Runs hybrid analysis
- Shows detailed results with reasoning

#### `/evaluate_context` (GET/POST)
- Displays analysis results
- GET: Shows analysis with correction form
- POST: Handles user corrections and reanalysis

**Correction Workflow**:
```
User sees wrong result → Fills correction form → Submits corrections
    ↓
System saves to corrections.json
    ↓
Runs fresh analysis with correction hints
    ↓
Shows updated results with "reanalyzed" flag
```

#### `/` and `/wizard` routes
- Multi-step wizard for detailed submission
- Collects title, description, impact, attachments
- Runs same analysis pipeline

### 5. AI Services

#### LLM Classifier (`llm_classifier.py`)
- Azure OpenAI GPT-4 integration
- Structured classification with reasoning
- Incorporates pattern features and corrections

#### Embedding Service (`embedding_service.py`)
- Text-to-vector conversion
- Uses Azure OpenAI embedding model
- Enables semantic similarity search

#### Vector Search (`vector_search.py`)
- In-memory vector database
- Stores historical issues as embeddings
- Fast cosine similarity search

### 6. Azure DevOps Integration (`ado_integration.py`)

**Purpose**: Query ADO work items for matching

**Features**:
- Azure CLI authentication (development)
- Service Principal support (production-ready)
- WIQL query construction
- Work item fetching and caching

**Query Types**:
- Search by text (title/description)
- Search by tags
- Filter by type (UAT, Feature, Bug)
- Filter by state (Active, Resolved, etc.)

## Data Flow

### Complete Analysis Pipeline

```
1. USER SUBMITS ISSUE
   ├─ Title: "Need Azure OpenAI capacity in West US"
   ├─ Description: "We need 10K TPM for gpt-4..."
   └─ Impact: "Blocking production deployment"

2. HYBRID ANALYZER RECEIVES REQUEST
   └─ hybrid_context_analyzer.analyze(title, description, impact)

3. PATTERN ANALYSIS (Always First)
   ├─ Extract domain entities → {"services": ["Azure OpenAI"], "regions": ["West US"]}
   ├─ Classify category → IssueCategory.AOAI_CAPACITY (confidence: 0.90)
   ├─ Classify intent → IntentType.CAPACITY_REQUEST (confidence: 0.95)
   ├─ Generate semantic keywords → ["capacity", "quota", "tpm", "gpt-4"]
   ├─ Assess urgency → "high" (has "blocking")
   └─ Recommend search strategy → prioritize_uats=True, prioritize_features=True

4. FIND RELEVANT CORRECTIONS
   ├─ Match corrections by word overlap
   ├─ Found 1 relevant correction about capacity requests
   └─ Add to features

5. AI CLASSIFICATION (If Available)
   ├─ Build prompt with:
   │  ├─ Issue text
   │  ├─ Pattern features
   │  └─ Relevant corrections
   ├─ Call GPT-4 → Classification + Reasoning
   ├─ Parse response → category="capacity", intent="capacity_request", confidence=0.98
   └─ Check agreement with pattern → agreement=True (both said "capacity")

6. SIMILARITY SEARCH
   ├─ Generate embedding for issue text
   ├─ Search vector database
   └─ Find 5 most similar historical issues

7. COMPILE RESULT
   └─ HybridAnalysisResult with all data

8. ENHANCED MATCHING SEARCH
   ├─ Use recommended_search_strategy → search ADO UATs and Features
   ├─ Generate intelligent search terms using semantic_keywords
   ├─ Search ADO: "Azure OpenAI capacity quota TPM limit"
   ├─ Search retirements: (skipped, not retirement issue)
   └─ Score and rank results

9. RETURN TO USER
   ├─ Display category: "Capacity"
   ├─ Display intent: "Capacity Request"
   ├─ Show AI reasoning: "User is requesting capacity increase..."
   ├─ Show confidence: 98%
   ├─ Show matching work items
   └─ Offer correction form if wrong
```

## Corrective Learning System (Phase 1)

### Current Implementation

**File**: `corrections.json`

**Structure**:
```json
{
  "corrections": [
    {
      "timestamp": "2025-12-31T12:00:00",
      "original_title": "Issue with Azure deployment",
      "original_category": "technical_support",
      "original_intent": "seeking_guidance",
      "correct_category": "service_availability",
      "correct_intent": "requesting_service",
      "correct_business_impact": "high",
      "user_feedback": "Actually a service availability question",
      "issue_description": "Full description...",
      "impact": "Business impact..."
    }
  ]
}
```

**How It Works**:

1. **User Marks Analysis as Wrong**
   - Selects correct category from dropdown
   - Selects correct intent from dropdown
   - Enters feedback description
   - Clicks "Reanalyze with Corrections"

2. **System Saves Correction**
   - Appends to corrections.json with timestamp
   - Stores original classification + correct classification
   - Stores user feedback and full issue text

3. **Correction Used in Future Analysis**
   - When analyzing new issue, finds similar corrections
   - Includes correction examples in LLM prompt
   - "Previously, user indicated similar issue should be..."
   - LLM learns from pattern and adjusts classification

4. **Reanalysis**
   - Runs fresh analysis with correction hints
   - Usually results in correct classification
   - Shows "reanalyzed" flag on results page

### Phase 2 Roadmap (Not Yet Implemented)

Future enhancements for production:
- **Correction Validation**: Verify corrections make sense
- **Quality Scoring**: Track correction effectiveness
- **Conflict Resolution**: Handle contradictory corrections
- **Duplicate Detection**: Merge similar corrections
- **Analytics Dashboard**: View correction patterns
- **Bulk Import/Export**: Manage corrections at scale

## Configuration

### Environment Variables

Required for AI features:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-standard  # Your GPT-4 deployment name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002  # Embedding model
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure DevOps (Optional - for ADO integration)
ADO_ORGANIZATION=your-org
ADO_PROJECT=your-project
ADO_PAT=your-personal-access-token

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
```

### Feature Flags

In code configuration:

```python
# Enable/disable AI
analyzer = HybridContextAnalyzer(use_ai=True)  # Set to False for pattern-only

# Enable/disable semantic search
result = analyzer.analyze(title, description, impact, search_similar=True)
```

## Error Handling

### Graceful Degradation

The system is designed to degrade gracefully when services are unavailable:

1. **Azure OpenAI Unavailable**:
   - System falls back to pattern matching
   - Confidence typically 50-90% vs 95%+ with AI
   - Still provides classification and routing

2. **Pattern Analyzer Error**:
   - Return default "technical_support" category
   - Medium confidence
   - Log error for investigation

3. **ADO Connection Failed**:
   - Skip ADO search
   - Search only retirements and vector database
   - Show warning to user

4. **Vector Search Unavailable**:
   - Skip similarity search
   - Continue with text-based matching
   - Results still useful

### Error Logging

All errors are logged to console with context:
```python
print(f"[HybridAnalyzer] LLM classification failed: {e}")
print(f"   ↩️  Falling back to pattern matching")
```

## Performance Considerations

### Speed Optimization

1. **Pattern-First Strategy**:
   - Fast baseline results (< 100ms)
   - Continues to AI while showing progress

2. **Parallel Operations**:
   - ADO, retirements, vector search run in parallel
   - Reduces total latency

3. **Caching**:
   - Vector embeddings cached in memory
   - ADO query results cached per session
   - Corrections loaded once at startup

### Scalability

Current limitations:
- In-memory vector database (not persistent)
- Single-threaded Flask development server
- No request queuing

Production recommendations:
- Use gunicorn/uwsgi for Flask
- Implement Redis for caching
- Use persistent vector database (Pinecone, Weaviate)
- Add request queuing (Celery)

## Testing Strategy

### Manual Testing Workflow

1. Submit test issue via Quick ICA form
2. Verify analysis results (category, intent, confidence)
3. Check reasoning makes sense
4. Review matched work items
5. If wrong, submit correction
6. Verify reanalysis corrects the issue
7. Submit similar issue to confirm learning

### Test Cases

Key scenarios to validate:
- Capacity requests (should route to capacity)
- Retirement questions (should find retirement docs)
- Technical support (should find UATs)
- Feature requests (should find features)
- Service availability (should check regions)
- Ambiguous issues (should ask for clarification)

## Deployment

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
# (add to .env file or export)

# Run Flask development server
python app.py
```

### Production

```bash
# Use production WSGI server
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Or uwsgi
uwsgi --http :8000 --wsgi-file app.py --callable app --processes 4
```

### Docker (Future)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## Monitoring

### Key Metrics to Track

1. **Classification Accuracy**:
   - % of issues correctly classified
   - Correction rate
   - Time to correction

2. **Confidence Scores**:
   - Average confidence by source (LLM vs pattern)
   - Distribution of confidence scores

3. **System Performance**:
   - Analysis latency (pattern, AI, total)
   - API error rates
   - Fallback frequency

4. **User Satisfaction**:
   - Correction submission rate
   - Matches clicked through
   - Issues resolved

### Logging Strategy

Current: Print to console
Recommended: Structured logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Analysis completed", extra={
    "category": result.category,
    "confidence": result.confidence,
    "source": result.source,
    "duration_ms": elapsed
})
```

## Security Considerations

### Current Implementation

- Azure CLI authentication (development only)
- API keys in environment variables
- No input validation/sanitization
- No rate limiting
- No authentication on web interface

### Production Requirements

1. **Authentication**:
   - Add user authentication (Azure AD, OAuth)
   - Role-based access control
   - Audit logging

2. **Input Validation**:
   - Sanitize user input
   - Limit input lengths
   - Validate file uploads

3. **API Security**:
   - Use Service Principal for ADO (not CLI)
   - Rotate keys regularly
   - Store secrets in Azure Key Vault

4. **Rate Limiting**:
   - Limit requests per user/IP
   - Prevent abuse of AI services
   - Queue expensive operations

## Troubleshooting

### Common Issues

#### "Azure OpenAI deployment not found"
- Check AZURE_OPENAI_DEPLOYMENT name matches your deployment
- Verify deployment is in same region as endpoint
- Confirm API version is correct

#### "Corrections not being applied"
- Check corrections.json exists and is valid JSON
- Verify corrections have required fields
- Ensure word overlap threshold met (3+ words)

#### "Low confidence scores"
- Check if AI is enabled (should be 95%+)
- Verify pattern analyzer has domain knowledge for category
- Review if issue description provides enough context

#### "No matches found"
- Check ADO connection
- Verify work items exist with relevant tags
- Try broader search terms

## Future Enhancements

### Short Term (Phase 2)

- Correction validation and quality scoring
- Admin dashboard for corrections management
- Bulk correction import/export
- Enhanced analytics and reporting

### Medium Term

- Persistent vector database
- Real-time learning (immediate correction application)
- Multi-language support
- Integration with more data sources

### Long Term

- Automated testing framework
- A/B testing for algorithm improvements
- Predictive routing (before full analysis)
- Self-service correction review system
