# Analysis Engine Flow - Complete Data Journey

## Overview
When a user enters **Title**, **Description**, and **Impact**, here's exactly what happens:

---

## 📊 COMPLETE ANALYSIS FLOW

### **ENTRY POINT: User Submits Form**
```
User Input:
├─ Title: "Azure OpenAI capacity needed in Australia East"
├─ Description: "Customer needs GPT-4 access for production workload..."
└─ Impact: "High-value customer, $2M deal at risk..."
```

---

## 🔄 STEP-BY-STEP DATA FLOW

### **1. app.py → `/quick_ica` Route** (Lines 1085-1123)
**What Happens:**
- Receives form POST request
- Extracts `title`, `description`, `impact` fields
- Validates that title and description are present
- Logs input data for debugging

**Data Sources Used:** NONE (just validation)

**Next:** Calls `EnhancedMatcher.analyze_context_for_evaluation()`

---

### **2. enhanced_matching.py → `analyze_context_for_evaluation()`** (Lines 1774-1820)
**What Happens:**
- Creates EnhancedMatcher instance
- Passes data to IntelligentContextAnalyzer

**Data Sources Used:** NONE (just orchestration)

**Next:** Calls `IntelligentContextAnalyzer.analyze_context()`

---

### **3. intelligent_context_analyzer.py → `analyze_context()`** (Lines 300-500)
**THIS IS THE CORE AI ENGINE - 10-STEP ANALYSIS PROCESS**

#### **Step 1: Basic Text Preprocessing**
**What Happens:**
- Combines title + description + impact into single text
- Converts to lowercase
- Tokenizes into words
- Removes stopwords
- Extracts key terms

**Data Sources:**
- ✅ **Python built-in libraries**: `re`, `str.lower()`, `str.split()`
- ✅ **Stopwords list**: Hardcoded in the analyzer

**Libraries Used:**
- Standard Python `re` (regex)
- String manipulation functions

---

#### **Step 2: Domain Entity Extraction** (Lines 360-450)
**What Happens:**
- Scans text for Azure services (e.g., "Azure OpenAI", "Defender for Cloud")
- Identifies compliance frameworks (NIST, PCI-DSS, HIPAA, GDPR, etc.)
- Extracts Microsoft products (Teams, SharePoint, Office 365, etc.)
- Detects regions/countries (Australia East, West Europe, etc.)

**Data Sources:**
- ✅ **Live Azure Services API** (cached in `.cache/azure_services.json`)
  - Source: `https://azure.microsoft.com/api/v3/services`
  - Fetches all Azure service names
  
- ✅ **Live Azure Regions API** (cached in `.cache/azure_regions.json`)
  - Source: Azure Management API
  - Lists all Azure regions/geos
  
- ✅ **Hardcoded Compliance Frameworks** (in code)
  - NIST 800-53, PCI-DSS, HIPAA, GDPR, SOC 2, ISO 27001, etc.
  
- ✅ **Microsoft Products List** (hardcoded)
  - Teams, SharePoint, Planner, Power BI, etc.

**Libraries Used:**
- `requests` - HTTP calls to Azure APIs
- `json` - Parse API responses
- `pathlib.Path` - File caching

---

#### **Step 3: Retirement Detection** (Lines 950-1100)
**What Happens:**
- Checks if user is asking about a retired/deprecated service
- Fuzzy matching against retirement database
- Returns retirement details if found (date, replacement service, etc.)

**Data Sources:**
- ✅ **retirements.json** (2,000+ service retirements)
  - Loaded from local file
  - Contains: service name, retirement date, replacement info, announcement URL
  
**Libraries Used:**
- `json` - Load retirement database
- `difflib.SequenceMatcher` - Fuzzy string matching

---

#### **Step 4: Microsoft Product Context Detection** (Lines 1451-1614)
**What Happens:**
- Detects Microsoft product mentions (Office 365, Teams, Planner, etc.)
- **Context-aware** - distinguishes between:
  - Product demos ("demo of Planner & Roadmap")
  - Technical issues ("Planner not working")
  - Timeline inquiries ("when will Planner support X?")

**Data Sources:**
- ✅ **Microsoft Products Dictionary** (hardcoded in code)
  - Maps: "office 365", "m365", "teams", "sharepoint", etc.

**Libraries Used:**
- Python `re` (regex pattern matching)
- String similarity algorithms

---

#### **Step 5: Corrective Learning Application** (Lines 1200-1350)
**What Happens:**
- Checks if similar issues were corrected before
- Loads user corrections from database
- Applies learned patterns to improve classification

**Data Sources:**
- ✅ **corrections.json** (user feedback database)
  - Stores: original classification → corrected classification
  - Includes: reasoning for correction
  
**Libraries Used:**
- `json` - Load corrections database
- Similarity matching algorithms

---

#### **Step 6: Category Classification** (Lines 1615-1850)
**What Happens:**
- **Scores each category** based on keywords and patterns:
  - Compliance/Regulatory (NIST, GDPR, audit, etc.)
  - Technical Support (error, issue, not working, etc.)
  - Feature Request (need, want, request, etc.)
  - Service Retirement (deprecated, end-of-life, etc.)
  - Service Availability (not available in, need in region, etc.)
  - AOAI Capacity (quota, capacity, TPM, RPM, etc.)
  - Roadmap (timeline, when available, future plans, etc.)
  - And 15+ more categories...

**Data Sources:**
- ✅ **Pattern dictionaries** (hardcoded keyword lists)
  - Each category has weighted keywords
  - Context-aware scoring (e.g., "roadmap" in technical issue = low weight)

**Libraries Used:**
- Python string matching
- Confidence scoring algorithms

**Example Scoring:**
```python
# For "Azure OpenAI capacity needed in Australia East"
AOAI_CAPACITY: 0.9 (keywords: "capacity", "Azure OpenAI")
SERVICE_AVAILABILITY: 0.7 (keywords: "needed in", "Australia East")
TECHNICAL_SUPPORT: 0.3 (no error keywords)
ROADMAP: 0.2 (no timeline keywords)
→ Winner: AOAI_CAPACITY (0.9)
```

---

#### **Step 7: Intent Classification** (Lines 1851-2050)
**What Happens:**
- Determines what the user wants to accomplish:
  - `seeking_guidance` - need advice/direction
  - `reporting_issue` - something is broken
  - `requesting_feature` - want new functionality
  - `capacity_request` - need more quota/capacity
  - `roadmap_inquiry` - when will X be available?
  - And 10+ more intents...

**Data Sources:**
- ✅ **Intent patterns** (hardcoded keyword lists)
  - Verb-based detection ("need", "want", "request", "error", "not working")
  - Context-aware (checks if it's a demo request vs. production issue)

**Libraries Used:**
- Python string matching
- Pattern recognition

---

#### **Step 8: Confidence Scoring** (Lines 2100-2200)
**What Happens:**
- Calculates overall confidence (0.0-1.0)
- Based on:
  - Number of matched keywords
  - Clarity of input text
  - Entity detection success
  - Category/intent agreement

**Data Sources:** NONE (algorithmic calculation)

**Libraries Used:**
- Mathematical scoring algorithms

---

#### **Step 9: Business Impact & Technical Complexity Assessment** (Lines 2250-2400)
**What Happens:**
- Analyzes business impact: `critical`, `high`, `medium`, `low`
- Assesses technical complexity: `high`, `medium`, `low`
- Determines urgency: `urgent`, `high`, `medium`, `low`

**Keywords checked:**
- Business Impact: "customer", "revenue", "deal", "production", "outage"
- Technical Complexity: "custom integration", "migration", "security", "compliance"
- Urgency: "urgent", "ASAP", "blocked", "critical"

**Data Sources:**
- ✅ **Impact/urgency keywords** (hardcoded)

**Libraries Used:**
- Keyword frequency analysis

---

#### **Step 10: Search Strategy Recommendation** (Lines 2450-2550)
**What Happens:**
- Recommends which data sources to search based on analysis:
  - `should_check_retirements`: True if service retirement detected
  - `should_search_uats`: True if looking for similar issues
  - `should_search_features`: True if feature request
  - `prioritize_azure_docs`: True if needs technical guidance

**Data Sources:** NONE (logic-based recommendation)

**Libraries Used:** NONE (rule-based logic)

---

## 📦 COMPLETE DATA SOURCES SUMMARY

### **External APIs** (Live, cached locally)
1. ✅ **Azure Services API** 
   - URL: `https://azure.microsoft.com/api/v3/services`
   - Cached: `.cache/azure_services.json`
   - Purpose: Service name detection

2. ✅ **Azure Regions API**
   - Source: Azure Management API
   - Cached: `.cache/azure_regions.json`
   - Purpose: Region/geography detection

### **Local JSON Databases**
3. ✅ **retirements.json** (2,000+ entries)
   - Service retirements/deprecations
   - Replacement recommendations
   - Announcement URLs

4. ✅ **corrections.json** (user feedback)
   - Historical corrections
   - Learning patterns
   - Classification improvements

5. ✅ **context_evaluations.json** (evaluation history)
   - Past analysis results
   - User approvals/rejections
   - Feedback for continuous improvement

### **Hardcoded Knowledge** (In Python code)
6. ✅ **Compliance Frameworks List**
   - NIST, PCI-DSS, HIPAA, GDPR, SOC 2, ISO 27001, FedRAMP, etc.

7. ✅ **Microsoft Products Dictionary**
   - Office 365, Teams, SharePoint, Planner, Roadmap, Power BI, etc.

8. ✅ **Category Keywords** (20+ categories)
   - Each category has 20-50 weighted keywords

9. ✅ **Intent Patterns** (15+ intents)
   - Verb-based patterns, context indicators

10. ✅ **Stopwords List**
    - Common words to ignore during analysis

### **Optional External Tools** (Not currently active)
11. ❌ **Microsoft Learn API** (imported but not used)
    - Would provide documentation search
    - Currently: `MICROSOFT_DOCS_AVAILABLE = False` (import fails)

---

## 🔧 PYTHON LIBRARIES USED

### **Core Python (Built-in)**
- `re` - Regular expressions for pattern matching
- `json` - JSON parsing for databases
- `datetime` - Timestamp handling
- `pathlib.Path` - File path management
- `dataclasses` - Data structure definitions
- `enum.Enum` - Category/Intent enumerations
- `typing` - Type hints
- `difflib.SequenceMatcher` - Fuzzy string matching

### **External Dependencies**
- `requests` - HTTP API calls (Azure APIs)
- `logging` - Debug logging

### **NOT Used** (despite imports)
- `subprocess` - Imported but unused
- Microsoft Learn APIs - Imported but disabled

---

## 🎯 OUTPUT FORMAT

After all 10 steps complete, returns **ContextAnalysis object**:

```python
ContextAnalysis(
    category = IssueCategory.AOAI_CAPACITY,
    intent = IntentType.CAPACITY_REQUEST,
    confidence = 0.85,
    
    domain_entities = {
        "azure_services": ["Azure OpenAI"],
        "regions": ["Australia East"],
        "products": []
    },
    
    key_concepts = [
        "capacity", "GPT-4", "production", "quota"
    ],
    
    business_impact = "high",  # Based on "$2M deal"
    technical_complexity = "medium",
    urgency_level = "high",  # Based on "at risk"
    
    recommended_search_strategy = {
        "should_check_retirements": False,
        "should_search_uats": True,
        "should_search_features": False,
        "prioritize_azure_docs": False
    },
    
    semantic_keywords = [
        "azure openai", "capacity", "australia east", "gpt-4"
    ],
    
    context_summary = "AOAI capacity request for Australia East region with high business impact",
    
    reasoning = {
        "category": "High AOAI keyword density + region mention",
        "intent": "Explicit capacity request language detected",
        "confidence": "Strong service and region entity extraction"
    }
)
```

---

## 🔍 WHAT HAPPENS NEXT?

After analysis completes:
1. **Results displayed to user** for validation
2. If approved → **Search phase begins**:
   - Search Azure DevOps for similar UATs (if recommended)
   - Check retirements database (if recommended)
   - Search feature requests (if recommended)
3. **Matching & Ranking** similar issues
4. **Display recommendations** to user

---

## 📝 KEY TAKEAWAYS

### **Analysis is 90% Local**
- Most analysis uses hardcoded patterns and local databases
- Only Azure service/region names come from live APIs (and are cached)

### **No AI Models** (Despite the name!)
- "AI-Powered" = sophisticated pattern matching + rule-based logic
- No OpenAI, no ML models, no neural networks
- Just very smart keyword detection with context awareness

### **Fast & Offline-Capable**
- Once APIs are cached, works fully offline
- No external dependencies during analysis
- All pattern matching is local

### **Learning System**
- Improves over time via corrections.json
- User feedback directly updates classification logic
- Corrective learning applied on every analysis

---

## 🚀 PERFORMANCE

**Typical Analysis Time:**
- Step 1-2 (Preprocessing): <0.1 seconds
- Step 3-5 (Entity extraction): 0.2-0.5 seconds
- Step 6-7 (Classification): 0.1-0.3 seconds
- Step 8-10 (Scoring): <0.1 seconds
- **Total: ~0.5-1.0 seconds**

**Bottlenecks:**
- None! All local operations are fast
- API calls only happen once (then cached)
