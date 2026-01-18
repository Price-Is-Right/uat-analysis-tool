# ICA API Testing Guide - Nightingale Collection

## Setup Nightingale Environment

1. **Create Environment Variables:**
   - Name: `ICA Local`
   - Variables:
     - `base_url` = `http://localhost:5002`
     - `api_version` = `v1`
     - `api_base` = `{{base_url}}/api/{{api_version}}`

---

## API Endpoint Tests

### 1. Quality Analysis API

**Endpoint:** `POST {{api_base}}/analyze/quality`

**Test 1: Valid Input - Good Quality**
```json
{
  "title": "Azure OpenAI capacity needed in West Europe for healthcare application",
  "description": "We are developing a healthcare chatbot using Azure OpenAI GPT-4 for a German hospital. The application needs to process patient inquiries about appointments, prescriptions, and medical procedures. Due to GDPR requirements, all data must remain in the EU. We need deployment in West Europe region with 100K TPM capacity for production workload.",
  "impact": "Blocking 50 enterprise customers. Critical for Q1 2026 compliance deadline. Potential revenue impact of $500K if not resolved."
}
```
**Expected:** `score: 95+`, minimal suggestions

**Test 2: Low Quality Input**
```json
{
  "title": "Need Azure OpenAI",
  "description": "We want to use GPT-4",
  "impact": ""
}
```
**Expected:** `score: <60`, multiple suggestions

**Test 3: Missing Required Field**
```json
{
  "title": "Test issue"
}
```
**Expected:** `400 error`, "Description is required"

---

### 2. Context Analysis API

**Endpoint:** `POST {{api_base}}/analyze/context`

**Test 1: Feature Request - Regional Availability**
```json
{
  "title": "Azure OpenAI needed in West Europe",
  "description": "We need GPT-4 deployment for GDPR-compliant healthcare chatbot in Germany",
  "impact": "Blocking production launch"
}
```
**Expected:** 
- `category: "feature_request"`
- `intent: "regional_availability"`
- `confidence: >0.8`
- `detected_products: ["Azure OpenAI"]`

**Test 2: Technical Support**
```json
{
  "title": "Azure Function deployment failing with error 500",
  "description": "Getting internal server error when deploying function app to consumption plan. Tried multiple regions.",
  "impact": "Production deployment blocked"
}
```
**Expected:**
- `category: "technical_support"`
- `confidence: >0.7`

**Test 3: Capacity Request**
```json
{
  "title": "Increase Azure OpenAI TPM quota",
  "description": "Current quota of 60K TPM insufficient for production workload. Need 300K TPM for GPT-4 deployment.",
  "impact": "Performance degradation affecting 100+ users"
}
```
**Expected:**
- `category: "capacity_request"` or `"aoai_capacity"`
- `intent: "capacity_increase"`

---

### 3. Resource Search API

**Endpoint:** `POST {{api_base}}/search/resources`

**Test 1: Full Search**
```json
{
  "title": "Azure OpenAI needed in West Europe",
  "description": "Healthcare chatbot requiring GDPR compliance",
  "category": "feature_request",
  "intent": "regional_availability",
  "domain_entities": {
    "services": ["Azure OpenAI"],
    "regions": ["West Europe"],
    "compliance": ["GDPR"]
  }
}
```
**Expected:**
- `learn_docs`: Array of Microsoft Learn articles
- `similar_products`: Alternative services
- `regional_options`: Available regions
- `retirement_info`: null (Azure OpenAI not retiring)

---

### 4. ADO Search APIs

**Endpoint 1:** `POST {{api_base}}/ado/search/features`

**Test: Search TFT Features**
```json
{
  "title": "Azure OpenAI West Europe availability",
  "description": "Need regional deployment",
  "limit": 5
}
```
**Expected:** Array of similar features with similarity scores

**Endpoint 2:** `POST {{api_base}}/ado/search/uats`

**Test: Search UATs**
```json
{
  "title": "Azure OpenAI capacity increase",
  "days_back": 180,
  "limit": 10
}
```
**Expected:** Array of similar UATs from last 180 days

---

### 5. UAT Creation API

**Endpoint:** `POST {{api_base}}/uat/create`

**Test: Create UAT (Use with caution - creates real work item!)**
```json
{
  "title": "TEST - Azure OpenAI West Europe - DELETE ME",
  "description": "This is a test UAT created via API. Please delete immediately.",
  "impact": "Test only",
  "category": "feature_request",
  "intent": "regional_availability",
  "selected_features": [],
  "selected_uats": [],
  "opportunity_id": "TEST123",
  "milestone_id": "2026-Q1"
}
```
**Expected:** 
- `success: true`
- `work_item_id`: numeric ID
- `url`: ADO work item URL

**⚠️ Warning:** This creates a real work item. Delete it immediately after testing!

---

## Error Testing

### Invalid JSON
**Test:** Send malformed JSON
**Expected:** `400 error`

### Missing Content-Type
**Test:** Don't set `Content-Type: application/json`
**Expected:** `400 error` or `415 error`

### Server Error
**Test:** Send request while Flask app is stopped
**Expected:** Connection refused or timeout

---

## Success Criteria

✅ All endpoints return `200/201` for valid requests  
✅ All endpoints return appropriate error codes for invalid requests  
✅ Response format matches documented structure  
✅ API completes within reasonable time (<5s for analysis, <10s for search)  
✅ CORS headers present in responses  

---

## Nightingale Collection Structure

Create folders in Nightingale:
```
ICA API v4.0
├── 1. Quality Analysis
│   ├── Good Quality Input
│   ├── Low Quality Input
│   └── Missing Field Error
├── 2. Context Analysis
│   ├── Feature Request
│   ├── Technical Support
│   └── Capacity Request
├── 3. Resource Search
│   └── Full Search
├── 4. ADO Operations
│   ├── Search Features
│   └── Search UATs
├── 5. UAT Creation
│   └── Create Test UAT (⚠️ Caution)
└── Error Tests
    ├── Invalid JSON
    └── Missing Content-Type
```

---

## Next Steps After Testing

1. ✅ Verify all endpoints work in Nightingale
2. Document any issues found
3. Proceed to Phase 2: Teams Bot Project Setup
