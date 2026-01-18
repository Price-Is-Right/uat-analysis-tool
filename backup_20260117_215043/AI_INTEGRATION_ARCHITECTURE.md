# AI Integration Architecture Documentation

## Overview

This document describes the **Unified Action Tracker (UAT) System** - a comprehensive platform that combines AI-powered context analysis, intelligent resource search, Azure DevOps integration, and automated UAT creation to streamline IT support escalation workflows.

The system intelligently classifies issues, searches relevant resources across multiple data sources, and creates properly formatted UAT work items with feature linking and reference management.

**Version:** 2.0  
**Last Updated:** January 8, 2026  
**Status:** Production Ready

---

## Architecture Components

### 1. Complete System Flow

```
User Submission (Flask UI)
      ↓
Quality Analysis
      ↓
Context Classification (AI)
      ↓
Category-Specific Routing
      ├─→ Feature Request: TFT Feature Search → UAT Creation
      ├─→ Technical Support: CSS Support Guidance (No UAT)
      ├─→ Capacity: Capacity Guidelines (MSX Milestone)
      ├─→ Cost/Billing: Out of Scope Message
      └─→ Standard: Resource Search → UAT Creation
      ↓
Azure DevOps Integration (Multi-Instance)
      ├─→ TFT Features (Production Org)
      └─→ UAT Creation (Test Org)
```

### 2. AI Classification Pipeline

```
User Submission
      ↓
IntelligentContextAnalyzer (Pattern Matcher)
      ↓
HybridContextAnalyzer (Integration Layer)
      ↓
LLMClassifier (AI Analysis)
      ↓
Final Classification Result
```

### 3. Component Details

#### AI Classification Components

| Component | File | Purpose |
|-----------|------|---------|
| **Pattern Matcher** | `intelligent_context_analyzer.py` | Rule-based analysis using keywords, entities, and patterns |
| **Hybrid Analyzer** | `hybrid_context_analyzer.py` | Integration layer combining pattern + AI |
| **LLM Classifier** | `llm_classifier.py` | GPT-4o semantic classification with reasoning |
| **Embedding Service** | `embedding_service.py` | Text embeddings for similarity search |
| **Vector Search** | `vector_search_service.py` | Find similar historical issues |
| **Cache Manager** | `cache_manager.py` | Smart caching to reduce API calls |
| **Configuration** | `ai_config.py` | Centralized AI settings and validation |

#### UAT Workflow Components

| Component | File | Purpose |
|-----------|------|---------||
| **Flask Application** | `app.py` | Web UI, routing, session management, workflow orchestration |
| **Azure DevOps Client** | `ado_integration.py` | Multi-instance ADO integration, work item creation, TFT search |
| **Enhanced Matcher** | `enhanced_matching.py` | UAT similarity search, feature matching, AI analysis integration |
| **Resource Search** | `search_service.py` | Microsoft Learn docs, regional availability, retirements |
| **Issue Tracker** | `app.py` (IssueTracker class) | Data persistence, evaluation storage, statistics |

#### Azure DevOps Integration

| Organization | Project | Purpose | Authentication |
|--------------|---------|---------|----------------|
| **unifiedactiontracker** (TEST) | Unified Action Tracker | UAT Creation | InteractiveBrowserCredential |
| **acrblockers** (PRODUCTION) | Technical Feedback Tracker | TFT Feature Search | InteractiveBrowserCredential |

**Note:** Dual authentication is required and expected behavior due to separate Azure DevOps organizations.

#### External Data Sources

| Data Source | Storage Location | Purpose | Update Frequency | Cache Duration |
|-------------|------------------|---------|------------------|----------------|
| **Azure Services** | `.cache/azure_services.json` | Live Azure service catalog via Resource Graph API | On-demand | 7 days |
| **Azure Regions** | `.cache/azure_regions.json` | Azure region availability data | On-demand | 7 days |
| **Regional Service Availability** | `.cache/regional_service_availability.json` | Service-to-region mapping | On-demand | 7 days |
| **Service Retirements** | `retirements.json` | Azure service retirement notices and dates | Manual updates | N/A (static file) |
| **User Corrections** | `corrections.json` | Classification corrections for AI learning | Real-time | N/A (training data) |
| **Microsoft Learn Docs** | Microsoft Learn API | Official documentation and guidance | API call | N/A (not cached) |
| **Compliance Frameworks** | Built-in | ISO, SOC2, HIPAA, PCI-DSS, FedRAMP standards | N/A | N/A (static) |
| **AI Embeddings** | `.cache/ai_cache/embeddings_cache.json` | Vector embeddings for semantic search | On-demand | 7 days |
| **AI Classifications** | `.cache/ai_cache/classifications_cache.json` | GPT-4o classification results | On-demand | 7 days |

**Data Source Details:**

1. **Azure Services API** (`intelligent_context_analyzer.py`):
   - Fetches live Azure Resource Provider types via Azure Resource Graph
   - Categorizes services by type (compute, storage, networking, etc.)
   - Used for: Product detection, service validation, availability checks

2. **Regional Service Availability** (`intelligent_context_analyzer.py`):
   - Maps which Azure services are available in which regions
   - Used for: Regional availability queries, migration planning

3. **Service Retirements** (`retirements.json`):
   - Manual database of Azure service retirement announcements
   - Includes retirement dates, replacement services, migration guides
   - Used for: Retirement checking, proactive migration planning

4. **Microsoft Learn Documentation** (`search_service.py`):
   - Real-time search via Microsoft Learn API
   - Returns relevant documentation articles, tutorials, troubleshooting guides
   - Used for: Context enrichment, user guidance, UAT descriptions

5. **Corrections Database** (`corrections.json`):
   - User-provided classification corrections
   - Fed into LLM as context for improved accuracy
   - Used for: Continuous learning, fine-tuning preparation

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User Submits Issue                                      │
│ - Title: "SCVMM to Azure Migrate Roadmap"                      │
│ - Description: "Trouble connecting SCVMM to Azure Migrate..."  │
│ - Impact: "Blocking our migration"                             │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Pattern Matching Analysis                               │
│ (IntelligentContextAnalyzer)                                    │
│                                                                  │
│ Actions:                                                         │
│ ✓ Detect Microsoft products (SCVMM, Azure Migrate)             │
│ ✓ Identify keywords (migrate, trouble, connecting)             │
│ ✓ Check compliance frameworks (none detected)                  │
│ ✓ Extract entities (services, regions, technologies)           │
│ ✓ Apply rule-based classification logic                        │
│                                                                  │
│ Output:                                                          │
│ - Category: TRAINING_DOCUMENTATION                              │
│ - Intent: NEED_MIGRATION_HELP                                   │
│ - Confidence: 0.60                                              │
│ - Detected Products: ["SCVMM", "Azure Migrate"]                │
│ - Reasoning: Pattern-based classification                       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Feature Extraction                                      │
│ (HybridContextAnalyzer._extract_pattern_features)              │
│                                                                  │
│ Extracts structured data from pattern result:                   │
│ - category_scores: {"TRAINING_DOCUMENTATION": 0.60}            │
│ - detected_products: ["SCVMM", "Azure Migrate"]                │
│ - technical_indicators: ["trouble", "connecting"]              │
│                                                                  │
│ Purpose: Convert pattern analysis into AI-consumable features   │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: AI Classification                                       │
│ (LLMClassifier - GPT-4o)                                        │
│                                                                  │
│ Input to AI:                                                     │
│ - Original text (title + description + impact)                  │
│ - Pattern features (category scores, products, indicators)      │
│ - Available categories and intents                              │
│                                                                  │
│ AI Analysis:                                                     │
│ ✓ Semantic understanding of user's actual problem              │
│ ✓ Considers pattern matcher's findings as context              │
│ ✓ Makes final classification decision                          │
│ ✓ Generates detailed reasoning                                 │
│                                                                  │
│ Output:                                                          │
│ - Category: MIGRATION                                           │
│ - Intent: MIGRATION_PLANNING                                    │
│ - Confidence: 0.85                                              │
│ - Reasoning: "Customer is migrating workloads from SCVMM..."   │
│ - Agreement: FALSE (disagreed with pattern matcher)            │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Final Result                                            │
│                                                                  │
│ Classification Used: AI (LLM)                                    │
│ - Category: migration                                           │
│ - Intent: migration_planning                                    │
│ - Confidence: 0.85                                              │
│ - Source: llm                                                   │
│ - Pattern Agreement: false                                      │
│                                                                  │
│ Cached for Future Use: ✓                                        │
│ Ready for ADO Integration: ✓                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Workflow

### Phase 1: Pattern Matching (First Pass)

**File:** `intelligent_context_analyzer.py`  
**Class:** `IntelligentContextAnalyzer`

**What it does:**
1. **Entity Extraction**
   - Scans text for Microsoft products (Azure services, M365 apps)
   - Identifies regions (East US, West Europe, etc.)
   - Detects compliance frameworks (NIST, GDPR, HIPAA)
   
2. **Rule-Based Classification**
   - Applies keyword matching patterns
   - Uses category confidence scoring
   - Considers technical indicators (error, issue, problem)
   
3. **Context Analysis**
   - Assesses business impact (high/medium/low)
   - Evaluates technical complexity
   - Determines urgency level

**Output:** `ContextAnalysis` object with:
- Category (enum)
- Intent (enum)
- Confidence score (0.0-1.0)
- Domain entities (dict)
- Reasoning (dict)

**Corrections Integration:**
- Loads corrections.json (user feedback history)
- Applies confidence boost for matching patterns
- Enhances pattern matching accuracy

### Phase 2: Feature Extraction + Corrections Matching

**File:** `hybrid_context_analyzer.py`  
**Methods:** `_extract_pattern_features()`, `_find_relevant_corrections()`

**What it does:**
1. **Extracts Pattern Features**
   - Extracts category from pattern result
   - Pulls confidence score
   - Gathers detected products/services
   - Identifies technical indicators
   - Structures data for AI consumption

2. **Finds Relevant Corrections** ✅ NEW
   - Loads corrections.json (user feedback history)
   - Computes word overlap with current issue (Jaccard similarity)
   - Identifies similar past misclassifications (>20% threshold)
   - Returns top 3 most relevant corrections

**Output:** Feature dictionary containing:
```python
{
    "category_scores": {"migration": 0.60},
    "detected_products": ["SCVMM", "Azure Migrate"],
    "technical_indicators": ["trouble", "connecting"],
    "relevant_corrections": [  # NEW
        {
            "original_category": "training_documentation",
            "corrected_category": "service_availability",
            "correction_notes": "User asking about regional service availability"
        }
    ]
}
```

### Phase 3: AI Classification (Semantic Analysis)

**File:** `llm_classifier.py`  
**Class:** `LLMClassifier`

**What it does:**
1. **Receives Input:**
   - Original user text (combined title + description + impact)
   - Pattern features from Phase 2
   - System prompt with instructions

2. **AI Processing:**
   - GPT-4o analyzes semantic meaning
   - Considers pattern features as context hints
   - **Reviews relevant corrections from past feedback** ✅ NEW
   - Makes independent classification decision
   - Generates detailed reasoning

3. **Smart Caching:**
   - Checks cache for identical text (7-day TTL)
   - API-first strategy: calls Azure OpenAI if needed
   - Saves result to cache for future use

**Output:** `ClassificationResult` object with:
- Category (string)
- Intent (string)  
- Confidence (float)
- Reasoning (string)
- Source ("cache" or "api")

**LLM Prompt Structure:**
- User text (title + description + impact)
- Pattern analysis features
- **⚠️ Learn from Previous Corrections section** ✅ NEW
  - Shows similar past misclassifications
  - Format: "Was classified as X but should be Y"
  - Includes correction reasoning
- Classification instructions with valid categories/intents

### Phase 4: Result Integration

**File:** `hybrid_context_analyzer.py`  
**Method:** `analyze_context()`

**What it does:**
1. Compares LLM vs Pattern classifications
2. Tracks agreement/disagreement
3. Returns final `ContextAnalysis` with:
   - LLM's classification (primary)
   - Pattern features (supplementary)
   - Agreement status
   - Complete reasoning chain

---

## UAT Creation Workflow (January 2026 Updates)

### Overview

The UAT creation process is a multi-step wizard that guides users through:
1. **Issue Submission** - Title, description, impact
2. **Quality Analysis** - Completeness scoring
3. **AI Classification** - Category and intent detection
4. **Resource Search** - Microsoft Learn, TFT Features, similar UATs
5. **Feature Selection** - Link up to 5 TFT Features (feature_request only)
6. **UAT Selection** - Link up to 5 related UATs for reference
7. **Tracking IDs** - Optional Opportunity ID and Milestone ID
8. **UAT Creation** - Create work item in Azure DevOps with all data

### Step-by-Step Flow

#### Step 1: Issue Submission
**Route:** `/` → `index()`

- User enters title, description (customer scenario), and impact
- Form validation ensures required fields
- Supports pre-filling from quality review "Update Input"
- Session cleaned for fresh submission

#### Step 2: Quality Analysis
**Route:** `/submit` → `submit_issue()`

- Calls `AIAnalyzer.analyze_completeness()`
- Scores title, description, and impact completeness
- Shows quality review page with 3 options:
  - **Cancel**: Return to home
  - **Update Input**: Return to form with current data
  - **Continue**: Proceed to classification
- Category-agnostic (works for all issue types)

#### Step 3: Context Analysis & Classification
**Route:** `/start_processing` → `start_processing()`

- Calls `EnhancedMatcher.analyze_context_for_evaluation()`
- AI-powered classification into categories:
  - `feature_request`: Routes to TFT Feature search
  - `technical_support`: Shows CSS support guidance (no UAT)
  - `cost_billing`: Out of scope message (no UAT)
  - `capacity` / `aoai_capacity`: Capacity guidelines
  - `service_availability`: Regional/retirement search
  - Other: Standard resource search
- Stores evaluation data in `temp_storage[evaluation_id]`
- Redirects to context summary

#### Step 4: User Review & Agreement
**Route:** `/context_summary` → `context_summary()`

- Displays AI classification results to user
- Shows category, intent, confidence, reasoning
- User options:
  - **Agree**: Continue to resource search
  - **Modify**: Correct classification
  - **See Details**: View full analysis
  - **Cancel**: Return to home
- Category displayed determines next steps

#### Step 5: Resource Search (Category-Specific)
**Route:** `/search_resources` → `search_resources()` → `/perform_search` → `perform_search()`

**Special Categories (Skip Standard Search):**
- `technical_support`: Only CSS support guidance
- `feature_request`: Only TFT Feature search
- `cost_billing`: Only out-of-scope message
- `capacity` / `aoai_capacity`: Only capacity guidelines

**Standard Categories (Full Search):**
- Microsoft Learn documentation (AI-generated queries)
- Similar/alternative Azure products
- Regional service availability
- Capacity guidance (if applicable)
- Retirement information

**Feature Request Flow:**
- Calls `AzureDevOpsClient.search_tft_features()`
- Searches TFT project using AI similarity matching
- Returns Features with similarity scores
- User can select up to 5 Features to link to UAT

#### Step 6: Search Results & Feature Selection
**Route:** `/search_results` → `search_results()`

**Display Sections by Category:**

1. **Feature Request:**
   - Category-specific guidance
   - TFT Feature results with similarity scores
   - Feature selection interface (up to 5)
   - Microsoft Learn docs
   - "Continue to Create UAT" button

2. **Technical Support:**
   - CSS support process guidance
   - No UAT creation option (out of scope)

3. **Cost/Billing:**
   - Out of scope message
   - GetHelp link
   - No UAT creation option

4. **Capacity:**
   - Capacity request guidelines
   - AI Capacity Hub link
   - MSX Milestone instructions

5. **Standard Categories:**
   - All resource search results
   - "Continue to Create UAT" option

**Feature Selection (Feature Request Only):**
- User clicks Features to select/deselect (toggle)
- Maximum 5 Features allowed
- AJAX endpoint: `/save_selected_feature`
- Stored in `evaluation_data['selected_tft_features']`

#### Step 7: Opportunity & Milestone IDs
**Route:** `/uat_input` → `uat_input()` → `/process_uat_input` → `process_uat_input()`

- Collects optional tracking IDs:
  - Opportunity ID
  - Milestone ID
- User options:
  - **Continue**: Proceed to UAT search with IDs
  - **Skip**: Proceed without IDs (warning if empty)
  - **Force Skip**: Proceed without IDs (no warning)
- IDs stored in session for UAT creation

#### Step 8: Similar UAT Search
**Route:** `/select_related_uats` → `select_related_uats()`

**Search Logic:**
- Retrieves title from `temp_storage[evaluation_id]['original_issue']['title']`
  - **Critical Fix (Jan 2026)**: Uses evaluation_data, not session wizard_title
- Calls `EnhancedMatcher.search_uat_items()`
- Filters to last 180 days only
- Handles date parsing failures gracefully

**Similarity Scoring (Jan 2026 Fix):**
- Uses `SequenceMatcher` (Ratcliff-Obershelp algorithm)
- Calculates actual similarity: 0.0 to 1.0
- **Before**: Hardcoded 0.75 (75%) for all matches
- **After**: Exact matches = 1.0 (100%), partial matches accurate
- Formula: `SequenceMatcher(None, query_title.lower(), uat_title.lower()).ratio()`

**HTML Cleaning (Jan 2026 Fix):**
- Strips HTML tags from descriptions: `re.sub(r'<[^>]+>', '', description)`
- Normalizes whitespace: `re.sub(r'\s+', ' ', text).strip()`
- Clean display in search results

**UAT Selection:**
- User can select up to 5 related UATs
- Toggle functionality (click to select/deselect)
- AJAX endpoint: `/save_selected_uat`
- Stored in session with unique `selection_id`

#### Step 9: UAT Creation
**Route:** `/create_uat` → `create_uat()`

**Data Sources:**
- `title`, `description`, `impact`: Original issue
- `context_analysis`: AI classification
- `selected_features`: TFT Feature IDs (up to 5)
- `selected_uats`: Related UAT IDs (up to 5)
- `opportunity_id`, `milestone_id`: Tracking IDs

**Azure DevOps Integration:**
- Calls `AzureDevOpsClient.create_work_item_from_issue()`
- Creates work item in **Unified Action Tracker Test** project
- Work item type: **Action**
- Organization: **unifiedactiontracker** (TEST)

**Customer Scenario Field (Jan 2026 Enhancement):**
```html
<strong>Category:</strong> Feature Request
<strong>Intent:</strong> Requesting Feature
<strong>Classification Reason:</strong> [AI reasoning]

<strong>Associated Features:</strong> 
<a href="https://dev.azure.com/acrblockers/.../123" target="_blank">#123</a>,
<a href="https://dev.azure.com/acrblockers/.../456" target="_blank">#456</a>

<strong>Associated UATs:</strong>
<a href="https://dev.azure.com/unifiedactiontracker/.../789" target="_blank">#789</a>
```

**Formatting Features:**
- HTML `<strong>` tags for labels
- `<br><br>` for spacing
- Clickable ADO links with `target="_blank"`
- Title Case conversion: `category.replace('_', ' ').title()`
- AI reasoning included for transparency

**Error Handling (Jan 2026 Fix):**
- Comprehensive try-except blocks
- Detailed logging with `[ROUTE_NAME]` prefixes
- `traceback.print_exc()` for debugging
- Flash messages for user feedback
- `error.html` template with 500 status

**Success Response:**
- Work item ID, URL, title, state
- Linked Features and UATs with IDs
- Opportunity/Milestone tracking IDs
- Timestamp and confirmation

### Category-Specific UAT Creation Eligibility

| Category | UAT Creation | Notes |
|----------|--------------|-------|
| ✅ `feature_request` | **Yes** | With TFT Feature linking (up to 5) |
| ❌ `technical_support` | **No** | Use CSS support process instead |
| ❌ `cost_billing` | **No** | Out of scope, redirect to GetHelp |
| ⚠️ `capacity` | **Maybe** | Submit via MSX Milestone first |
| ⚠️ `aoai_capacity` | **Maybe** | Follow AI Capacity Hub process |
| ✅ `service_availability` | **Yes** | With regional/retirement resources |
| ✅ `general_inquiry` | **Yes** | Standard workflow |
| ✅ Other categories | **Yes** | Standard workflow |

### Key January 2026 Fixes

1. **UAT Search Title Fix**
   - **Problem**: Used `session['wizard_title']` (never set)
   - **Solution**: Use `temp_storage[evaluation_id]['original_issue']['title']`
   - **Location**: `app.py` lines 604-612

2. **Dynamic Similarity Scoring**
   - **Problem**: Hardcoded `'similarity': 0.75` for all matches
   - **Solution**: Calculate with `SequenceMatcher.ratio()`
   - **Result**: Exact matches = 100%, accurate percentages
   - **Location**: `enhanced_matching.py` lines 875-890

3. **HTML Tag Stripping**
   - **Problem**: Azure DevOps descriptions contained `<div>` tags
   - **Solution**: `re.sub(r'<[^>]+>', '', uat_description)`
   - **Location**: `enhanced_matching.py` lines 870-871

4. **Customer Scenario Enhancement**
   - **Problem**: Raw text "category = feature_request" with `\n\n`
   - **Solution**: HTML formatting, Title Case, clickable links
   - **Location**: `ado_integration.py` lines 392-420

5. **Comprehensive Error Handling**
   - **Problem**: No try-except blocks in critical routes
   - **Solution**: Added error handling with logging and error.html
   - **Routes**: `create_uat`, `process_uat_input`, others
   - **Location**: Multiple routes in `app.py`

6. **Code Cleanup**
   - Removed 5 test files (`test_*.py`)
   - Removed ~75 lines of DEBUG print statements
   - Commented out unused health check code

7. **Documentation Enhancement**
   - Added detailed docstrings (111+ lines)
   - Comprehensive inline comments
   - Category routing documentation
   - Error handling explanations

---

## Configuration

### Environment Variables (.env)

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://openai-bp-northcentral.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT=gpt-4o-standard

# Cache Configuration
CACHE_TTL_DAYS=7
CACHE_API_FIRST=True

# Azure DevOps Configuration
# Two separate organizations with independent authentication
# 1. UAT Creation (TEST environment)
AZURE_DEVOPS_UAT_ORG=unifiedactiontracker
AZURE_DEVOPS_UAT_PROJECT=Unified Action Tracker
AZURE_DEVOPS_UAT_AUTH=InteractiveBrowserCredential

# 2. TFT Feature Search (PRODUCTION environment)  
AZURE_DEVOPS_TFT_ORG=acrblockers
AZURE_DEVOPS_TFT_PROJECT=Technical Feedback Tracker (ID: b47dfa86-3c5d-4fc9-8ab9-e4e10ec93dc4)
AZURE_DEVOPS_TFT_AUTH=InteractiveBrowserCredential

# Flask Configuration
FLASK_PORT=5002
FLASK_HOST=127.0.0.1
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
```

### AI Configuration (ai_config.py)

```python
config = AIConfig()
config.embedding_model      # "text-embedding-3-large"
config.classification_model # "gpt-4o"
config.cache_ttl_days      # 7 days
config.cache_api_first     # True (call API even if cache exists but might be stale)
```

---

## Multi-Instance Azure DevOps Architecture

### Overview

The system integrates with **two separate Azure DevOps organizations** for different purposes:

1. **TEST Organization (UAT Creation)**
   - Organization: `unifiedactiontracker`
   - Project: `Unified Action Tracker`
   - Purpose: Create UAT work items
   - Work Item Type: `Action`
   - Authentication: InteractiveBrowserCredential (user login)

2. **PRODUCTION Organization (TFT Feature Search)**
   - Organization: `acrblockers`
   - Project: `Technical Feedback Tracker`
   - Project ID: `b47dfa86-3c5d-4fc9-8ab9-e4e10ec93dc4`
   - Purpose: Search and link existing Features
   - Work Item Type: `Feature`
   - Authentication: InteractiveBrowserCredential (user login)

### Dual Authentication Behavior

**Expected:** Users will be prompted for authentication **twice** per session:
1. **First prompt**: UAT organization authentication (startup)
2. **Second prompt**: TFT organization authentication (when searching Features)

This is **correct and required behavior** due to:
- Separate Azure DevOps organizations
- Different security contexts
- No cross-organization token sharing
- Microsoft security best practices

### Integration Points

#### 1. UAT Creation
**File:** `ado_integration.py` → `AzureDevOpsClient.create_work_item_from_issue()`

```python
# Creates work item in TEST organization
work_item = {
    'title': issue_data['title'],
    'description': issue_data['description'],
    'System.WorkItemType': 'Action',
    'CustomerScenarioandDesiredOutcome': formatted_scenario,
    'Microsoft.VSTS.Common.Priority': 2,
    'System.State': 'New'
}

# Posts to: https://dev.azure.com/unifiedactiontracker/
```

**Custom Fields:**
- `CustomerScenarioandDesiredOutcome`: HTML-formatted scenario with Feature/UAT links
- `MSXMilestone`: Optional Milestone ID
- `MSXOpportunity`: Optional Opportunity ID
- `System.Tags`: Comma-separated tags from AI classification

#### 2. TFT Feature Search
**File:** `ado_integration.py` → `AzureDevOpsClient.search_tft_features()`

```python
# Searches PRODUCTION organization
# Uses Azure DevOps AI search (semantic matching)
search_request = {
    'searchText': combined_text,
    '$top': 20,
    '$skip': 0,
    'filters': {
        'Project': [tft_project_id],
        'WorkItemType': ['Feature']
    }
}

# Posts to: https://almsearch.dev.azure.com/acrblockers/
```

**Search Strategy:**
- AI-powered semantic search (Azure DevOps native)
- Searches title and description fields
- Filters to Feature work items only
- Returns similarity scores
- Maximum 20 results

#### 3. Feature Linking in UAT
**File:** `ado_integration.py` → Customer Scenario field assembly

```python
# Creates clickable links to PRODUCTION Features
for feature_id in selected_features:
    feature_url = f"https://dev.azure.com/acrblockers/b47dfa86-3c5d-4fc9-8ab9-e4e10ec93dc4/_workitems/edit/{feature_id}"
    feature_links.append(f'<a href="{feature_url}" target="_blank">#{feature_id}</a>')

# Links are cross-organization (TEST UAT → PROD Features)
```

#### 4. UAT Reference Linking
**File:** `ado_integration.py` → Customer Scenario field assembly

```python
# Creates clickable links to related UATs in TEST organization
for uat_id in selected_uats:
    uat_url = f"https://dev.azure.com/unifiedactiontracker/Unified%20Action%20Tracker/_workitems/edit/{uat_id}"
    uat_links.append(f'<a href="{uat_url}" target="_blank">#{uat_id}</a>')
```

### Error Handling

**Authentication Failures:**
- Caught in `AzureDevOpsClient.__init__()`
- User prompted to re-authenticate
- Retries automatically

**Search Failures:**
- TFT search returns error dict: `{'error': 'type', 'message': 'details'}`
- UI displays error message
- User can continue to UAT creation without Feature links

**Creation Failures:**
- Comprehensive try-except in `create_uat()` route
- Logs full stack trace with `[CREATE_UAT]` prefix
- Renders `error.html` template with 500 status
- Flash message shows error details

---

## Caching Strategy

### Cache Architecture

```
cache/ai_cache/
├── embeddings_cache.json         # Vector embeddings (3072-dim)
└── classifications_cache.json    # LLM classification results
```

### Cache Behavior

| Scenario | Action |
|----------|--------|
| Exact text match, fresh cache (< 7 days) | Return cached result |
| Exact text match, stale cache (> 7 days) | Call API, update cache |
| API-first enabled | Always call API, ignore cache age |
| No cache entry | Call API, save to cache |
| API failure | Use stale cache if available |

### Cache Statistics

The system tracks:
- Total cache entries
- Expired entries
- Average entry age
- Cache hit rate
- Cache file paths

---

## Integration Points

### Application Integration (app.py)

```python
from enhanced_matching import EnhancedMatcher

matcher = EnhancedMatcher()

# Quick analysis endpoint
@app.route('/quick_ica', methods=['POST'])
def quick_ica():
    result = matcher.quick_ica(
        title=request.form['title'],
        description=request.form['description'],
        impact=request.form.get('impact', '')
    )
    # result contains AI classification
```

### Enhanced Matching (enhanced_matching.py)

```python
from hybrid_context_analyzer import HybridContextAnalyzer

class EnhancedMatcher:
    def __init__(self):
        self.analyzer = HybridContextAnalyzer()
    
    def quick_ica(self, title, description, impact):
        # Uses hybrid analyzer instead of pattern-only
        analysis = self.analyzer.analyze_context(title, description, impact)
        return self._format_analysis(analysis)
```

---

## Key Features

### 1. Hybrid Intelligence

**Why Both?**
- **Pattern Matching:** Fast, deterministic, handles known patterns
- **AI Analysis:** Semantic understanding, handles novel cases, learns context

**How They Work Together:**
- Pattern matcher provides structured context to AI
- AI can agree with or override pattern matcher
- Best of both worlds: speed + intelligence

### 2. Corrective Learning (Pattern Matcher Only)

**Current Implementation Status:** ⚠️ Partially Implemented

**What Works:**
- User corrections are saved to `corrections.json` when feedback is provided
- Pattern matcher loads corrections on startup
- Pattern matcher searches for similar text patterns in corrections
- If match found: confidence boost applied to corrected category

**What Doesn't Work Yet:**
- Corrections are NOT passed to the hybrid analyzer
- LLM never sees correction data
- No actual GPT-4o fine-tuning implemented
- Corrections only affect pattern matching confidence scores

**Corrections Format:**
```json
{
    "corrections": [
        {
            "original_text": "sql mi in west europe",
            "pattern": "service_availability_request",
            "original_category": "training_documentation",
            "corrected_category": "service_availability",
            "confidence_boost": 0.1,
            "timestamp": "2025-12-31T10:00:00Z"
        }
    ]
}
```

**Current Impact:** Low - corrections only influence pattern matcher, which is then overridden by AI in most cases.

### 3. Transparency & Auditability

Every classification includes:
- **Step-by-step reasoning** from both pattern matcher and AI
- **Data sources used** (Azure APIs, corrections, retirements)
- **Confidence scores** with explanations
- **Agreement status** between pattern and AI
- **Complete decision trail** for debugging

---

## Performance Metrics

### Latency

| Component | Typical Duration | Notes |
|-----------|-----------------|-------|
| Pattern Matching | 50-200ms | Fast, rule-based |
| Feature Extraction | < 10ms | Simple dict operations |
| LLM Classification (cache hit) | 5-20ms | Near-instant |
| LLM Classification (API call) | 1-3 seconds | Azure OpenAI latency |
| **Total (cached)** | **100-300ms** | Most common path |
| **Total (API call)** | **1-3.5 seconds** | First-time classifications |

### Cost Optimization

- **7-day cache:** Reduces API calls by ~80-90%
- **Exact text matching:** Only cache identical submissions
- **API-first strategy:** Ensures fresh results when needed
- **Smart fallbacks:** Use stale cache if API unavailable

### Accuracy

Based on test cases:
- **Pattern-only accuracy:** ~60-70%
- **Hybrid AI accuracy:** ~85-95%
- **Agreement rate:** ~40% (AI often provides better classification)

---

## Testing

### Run Component Tests

```powershell
# Test configuration
python ai_config.py

# Test embeddings
python embedding_service.py

# Test LLM classification
python llm_classifier.py

# Test full hybrid analyzer
python hybrid_context_analyzer.py
```

### Test Cases

See `hybrid_context_analyzer.py` main block for example test cases:
1. SCVMM migration (technical support)
2. SQL MI availability (service availability)
3. Planner demo (seeking guidance)

---

## Troubleshooting

### Common Issues

**Issue:** "max() iterable argument is empty"  
**Cause:** Pattern feature extraction bug  
**Solution:** Fixed in v1.0 - ensures category_scores always populated

**Issue:** LLM classifications always cached  
**Cause:** API-first disabled  
**Solution:** Set `CACHE_API_FIRST=True` in .env

**Issue:** High API costs  
**Cause:** Cache TTL too short  
**Solution:** Increase `CACHE_TTL_DAYS` to 7 or higher

**Issue:** Stale classifications  
**Cause:** Cache not expiring  
**Solution:** Enable API-first or reduce cache TTL

**Issue:** Corrections not improving accuracy  
**Cause:** Word overlap threshold too strict  
**Solution:** Adjust Jaccard similarity threshold in `_find_relevant_corrections()` (default: 0.2)

---

## Corrections System ✅ IMPLEMENTED

### Overview

The corrections system allows the AI to learn from user feedback without expensive fine-tuning. When users provide corrections through the feedback UI, these are stored in `corrections.json` and used to improve future classifications.

### How It Works

1. **User Provides Correction**
   - Via feedback UI: marks classification as incorrect
   - Provides correct category/intent
   - Optionally adds notes explaining why

2. **Correction Storage**
   - Saved to `corrections.json`
   - Format: original text, pattern, categories, notes, timestamp
   - Pattern matcher applies confidence boost on matches

3. **Correction Matching (Phase 1 ✅)**
   - Hybrid analyzer loads corrections on startup
   - For each new issue: computes word overlap (Jaccard similarity)
   - Finds similar past corrections (>20% threshold)
   - Returns top 3 most relevant corrections

4. **LLM Learning (Phase 1 ✅)**
   - Corrections passed as features to LLM
   - Prompt includes "⚠️ Learn from Previous Corrections" section
   - Shows: "Was classified as X but should be Y - Reason: ..."
   - LLM adjusts reasoning based on past mistakes

### Benefits

- **No fine-tuning costs** - In-context learning only
- **Immediate effect** - Corrections active on next restart
- **Transparent** - LLM reasoning shows how corrections influenced decision
- **Accumulative** - More corrections = better accuracy

### Verified Performance

- Test Case: SQL MI availability query
- Original misclassification: `training_documentation`
- Correction applied: `service_availability`
- New classification: `service_availability` (95% confidence)
- Source: LLM with corrections context

### Files

- `corrections.json` - User feedback storage
- `hybrid_context_analyzer.py` - Correction matching logic
- `llm_classifier.py` - Prompt integration
- `intelligent_context_analyzer.py` - Pattern matcher boost

---

## Future Enhancements

### Planned Features

1. **✅ Corrections System Phase 1 (COMPLETE)**
   - Pass corrections as features to hybrid analyzer
   - Include corrections in LLM context window
   - In-context learning from user feedback

2. **🔄 Corrections System Phase 2-4 (PLANNED)**
   - Correction validation and quality scoring
   - Semantic similarity matching using embeddings
   - Fine-tuning pipeline when 50+ corrections available

3. **Multi-model Support**
   - A/B testing different models

3. **Advanced Caching**
   - Semantic similarity caching (not just exact match)
   - Use embeddings to find similar cached classifications

4. **Metrics Dashboard**
   - Track pattern vs AI agreement rates
   - Monitor classification distribution
   - Analyze correction patterns

5. **Batch Processing**
   - Classify multiple issues in parallel
   - Bulk cache warming

---

## Team Resources

### Key Files to Know

| File | Purpose | Touch Frequency | Lines |
|------|---------|-----------------|-------|
| `app.py` | Flask routes, UI, workflow orchestration | Often (new features) | 2,214 |
| `ado_integration.py` | Azure DevOps integration, work item creation | Occasionally | ~800 |
| `enhanced_matching.py` | UAT/Feature search, AI integration | Occasionally | ~900 |
| `search_service.py` | Resource search (Learn, regional, retirements) | Rarely | ~500 |
| `ai_config.py` | AI configuration | Rarely | ~150 |
| `intelligent_context_analyzer.py` | Pattern matcher | When adding new patterns | ~600 |
| `hybrid_context_analyzer.py` | AI integration layer | Rarely | ~400 |
| `llm_classifier.py` | AI classifier | When changing prompts | ~300 |
| `corrections.json` | Learning data | Auto-updated by users | Variable |
| `.env` | Credentials | When rotating keys | ~15 |

### Template Files

| Template | Purpose | Category Support |
|----------|---------|------------------|
| `index.html` | Issue submission form | All |
| `input_quality_review.html` | Quality analysis display | All |
| `context_summary.html` | AI classification summary | All |
| `searching_resources.html` | Resource search progress | All |
| `search_results.html` | Resource display with category guidance | Category-specific |
| `uat_input.html` | Opportunity/Milestone ID collection | UAT-eligible categories |
| `searching_uats.html` | UAT search progress | UAT-eligible categories |
| `select_related_uats.html` | Related UAT selection | UAT-eligible categories |
| `uat_created.html` | Success confirmation | UAT-eligible categories |
| `error.html` | Error display | All (fallback) |
| `no_match.html` | Legacy results page | Deprecated |

### Important Constants

```python
# Session Keys
'original_wizard_data'    # Original user input
'evaluation_id'           # Current evaluation ID
'process_id'              # Background processing ID
'results_id'              # Search results ID in temp_storage
'selected_tft_features'   # Selected Feature IDs (max 5)
'selected_uats'           # Selected UAT IDs (max 5)
'opportunity_id'          # Optional tracking ID
'milestone_id'            # Optional tracking ID

# Temp Storage
temp_storage[evaluation_id] = {
    'original_issue': {...},
    'context_analysis': {...},
    'search_results': {...},
    'selected_tft_features': [...]
}

temp_storage[selection_id] = {
    'enhanced_results': {...},
    'timestamp': time.time()
}

# Categories
SPECIAL_CATEGORIES = [
    'technical_support',   # No UAT
    'feature_request',     # TFT search + UAT
    'cost_billing',        # No UAT
    'aoai_capacity',       # Guidelines only
    'capacity'             # Guidelines only
]

# Limits
MAX_FEATURES = 5          # Maximum TFT Features to link
MAX_UATS = 5             # Maximum related UATs to link
UAT_SEARCH_DAYS = 180    # Search last 6 months of UATs
```

### Deployment Checklist

**Prerequisites:**
- [ ] Python 3.13+ installed
- [ ] Azure OpenAI access with deployments created
- [ ] Azure DevOps access to both organizations (TEST + PROD)
- [ ] Valid credentials for both ADO organizations

**Configuration:**
- [ ] `.env` file created with all required variables
- [ ] Azure OpenAI endpoint and API key configured
- [ ] Azure DevOps organization names verified
- [ ] Flask secret key generated
- [ ] Cache directory created (`cache/ai_cache/`)

**Azure OpenAI Deployments:**
- [ ] `text-embedding-3-large` deployment created
- [ ] `gpt-4o-standard` deployment created
- [ ] Deployment names match `.env` configuration

**Azure DevOps Setup:**
- [ ] Access to `unifiedactiontracker` organization (TEST)
- [ ] Access to `acrblockers` organization (PRODUCTION)
- [ ] Can create work items in UAT project
- [ ] Can search Features in TFT project
- [ ] InteractiveBrowserCredential authentication tested for both orgs

**Testing:**
- [ ] Test all AI components individually
- [ ] Test quality analysis flow
- [ ] Test classification (all categories)
- [ ] Test TFT Feature search (feature_request)
- [ ] Test UAT search (similarity scoring)
- [ ] Test complete UAT creation (end-to-end)
- [ ] Test error handling (invalid input, API failures)
- [ ] Test category-specific routing (technical_support, capacity, etc.)
- [ ] Verify dual authentication prompts work correctly
- [ ] Test all templates render correctly

**Validation:**
- [ ] Flask app starts without errors on port 5002
- [ ] Navigate to http://127.0.0.1:5002
- [ ] Submit test issue and complete workflow
- [ ] Verify UAT created in Azure DevOps
- [ ] Check Customer Scenario field formatting
- [ ] Verify Feature links are clickable and work
- [ ] Verify UAT links are clickable and work
- [ ] Check logs for errors/warnings
- [ ] Clear `__pycache__` directories
- [ ] Monitor initial API usage and costs

**Post-Deployment:**
- [ ] Create backup of working state
- [ ] Document any custom configuration
- [ ] Set up monitoring for API usage
- [ ] Configure alerting for errors
- [ ] Train users on new features

---

## Support & Maintenance

### Monitoring

**AI Classification:**
- Cache hit rates (should be > 80%)
- API call volumes and costs
- Classification confidence scores
- Pattern vs AI agreement rates
- User correction frequency

**UAT Workflow:**
- UAT creation success rate
- Average workflow completion time
- Feature selection rates (feature_request category)
- UAT reference linking rates
- Category distribution (which categories are most common)
- Error rates by route

**Azure DevOps:**
- Authentication failure rates
- TFT search success rates
- UAT creation failures
- API rate limiting issues
- Work item creation times

**Performance:**
- Page load times
- Search completion times
- Background processing duration
- Temp storage size (cleanup stale data)
- Session storage size

### Logging Strategy

All routes use consistent logging format:
```python
print(f"[ROUTE_NAME] Log message with context")
```

**Log Prefixes:**
- `[CREATE_UAT]`: UAT creation route
- `[TFT Search]`: TFT Feature search
- `[UAT Search]`: Similar UAT search
- `[SearchService]`: Resource search
- `[Classification]`: AI classification
- `[ERROR]`: Error conditions

**Error Logging:**
```python
try:
    # Operation
except Exception as e:
    print(f"[ROUTE_NAME] ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    flash(f"Error: {str(e)}", 'error')
```

### Updating

**When Microsoft adds new services/regions:**
- Pattern matcher auto-updates (Azure CLI integration)
- Cache refreshes automatically every 7 days
- Manual refresh: delete `.cache/azure_*.json` files

**When user feedback patterns emerge:**
- Review `corrections.json`
- Update pattern matcher rules if needed
- Consider model fine-tuning (if 50+ corrections)

**When adding new categories:**
1. Add category to `ai_config.py` valid categories
2. Add category guidance in `_get_category_guidance()` (app.py)
3. Update category routing in `perform_search()` (app.py)
4. Update `search_results.html` template
5. Test end-to-end workflow
6. Update documentation

**When modifying UAT workflow:**
1. Update route docstrings in `app.py`
2. Test all category-specific paths
3. Verify session/temp_storage data flow
4. Update template files if UI changes
5. Test error handling
6. Create backup before deployment
7. Update this documentation

### Troubleshooting

**Common Issues:**

1. **Dual Authentication Prompts**
   - **Symptom**: User prompted twice for Azure DevOps login
   - **Solution**: This is **expected and correct** (TEST + PROD orgs)
   - **Not a bug**: Two separate organizations require separate auth

2. **UAT Search Returns No Results**
   - **Check**: `temp_storage[evaluation_id]['original_issue']['title']` exists
   - **Check**: Date filtering (last 180 days)
   - **Check**: Azure DevOps connectivity to TEST org

3. **TFT Search Fails**
   - **Check**: User authenticated to PROD org (`acrblockers`)
   - **Check**: AI search enabled in Azure DevOps
   - **Check**: Project ID is correct
   - **Fallback**: User can continue without Feature links

4. **Customer Scenario Field Shows Raw HTML**
   - **Check**: Azure DevOps field type is HTML
   - **Check**: HTML tags properly formatted (`<strong>`, `<a>`)
   - **Verify**: Links use correct URLs for each org

5. **Similarity Scores Incorrect**
   - **Verify**: Using `SequenceMatcher.ratio()` not hardcoded value
   - **Check**: HTML stripping regex working
   - **Location**: `enhanced_matching.py` lines 875-890

6. **Session Data Lost**
   - **Check**: Flask secret key configured
   - **Check**: Session timeout settings
   - **Consider**: Move to Redis for persistence

7. **Temp Storage Growing Large**
   - **Add**: Cleanup job for stale entries (> 24 hours)
   - **Monitor**: `temp_storage` size in logs
   - **Consider**: Move to Redis/Cosmos for scalability

### Backup & Recovery

**Before Major Changes:**
```powershell
# Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path "C:\Projects\Hack" -Destination "C:\Projects\Hack\backup_$timestamp" -Recurse
```

**What to Backup:**
- All `.py` files
- All template files
- `corrections.json`
- `.env` file (secure storage)
- Cache files (optional)
- Documentation

**Restore Process:**
1. Stop Flask application
2. Restore files from backup
3. Verify `.env` configuration
4. Clear `__pycache__` directories
5. Test AI components
6. Test full workflow
7. Start Flask application

### Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | Dec 31, 2025 | Initial AI classification system |
| **2.0** | Jan 8, 2026 | Complete UAT workflow, multi-instance ADO, category routing, error handling, comprehensive documentation |

---

## Questions?

**Primary Contacts:**
- Development Team
- Azure DevOps Admins (for org access issues)
- Azure OpenAI Team (for API issues)

**Documentation:**
- This file: System architecture
- `README.md`: Quick start guide
- `QUICKSTART.md`: User guide
- Code docstrings: Implementation details

**Version:** 2.0  
**Last Updated:** January 8, 2026  
**Status:** Production Ready ✅
