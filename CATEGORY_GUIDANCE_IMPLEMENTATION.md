# Category-Specific Guidance Implementation

## Summary of Changes

Implemented category-specific guidance and TFT Feature search for the Enhanced Issue Tracker System.

## Features Added

### 1. **TFT Feature Search** (for `feature_request` category)
- Searches Technical Feedback ADO for existing Features
- Displays results with similarity scores (70% threshold)
- Allows users to select similar features
- Stores selected Feature IDs for UAT creation

### 2. **Category-Specific Guidance**

#### **technical_support**
```
This appears to be a Technical Support issue:

1. Please open a support case via https://aka.ms/csscompass
2. Work with your CSAM to follow the CSS "Escalate NOW" process through http://aka.ms/reactiveescalation
3. If all CSS escalation options are exhausted, submit a GetHelp through https://aka.ms/GetHelp
```

#### **feature_request**
- Searches TFT Features automatically
- Displays similar existing features with selection capability
- Stores selected Feature IDs for reference in UAT creation

#### **cost_billing**
```
It appears this issue falls outside the scope of our support. This forum is dedicated 
to technical escalations and is not equipped to address billing-related inquiries.

For assistance with billing, please submit your request through GetHelp at https://aka.ms/GetHelp.
```

#### **aoai_capacity**
```
Please review the guidelines for submitting an Azure OpenAI Capacity request:
https://aka.ms/aicapacityhub

This action will be completed from the Milestone in MSX.
```

#### **capacity**
```
For AI Capacity Requests:
All AI capacity requests should be made per the instructions at 
https://aka.ms/aicapacityhub#ai-infra-uat-submission-process from within the MSX Milestone.

Non-AI Capacity Requests:
Please ensure that a valid non-AI capacity escalation request is created following 
the published guidelines at [Capacity Escalation Process PowerPoint] and is done 
directly from within the MSX Milestone.
```

### 3. **Modified Search Flow**
For special categories (`technical_support`, `feature_request`, `cost_billing`, `aoai_capacity`, `capacity`):
- Skip Similar Products search
- Skip Regional Availability search
- Skip Capacity Guidance search (unless general capacity)
- Still search Microsoft Learn docs
- Display category-specific guidance prominently

## Files Modified

### 1. **ado_integration.py**
- Added `search_tft_features()` method to AzureDevOpsClient
- Searches Technical Feedback project for Features
- Returns matches with similarity scores

### 2. **app.py**
- Added `_get_category_guidance()` helper function
- Modified `/perform_search` route to:
  - Skip comprehensive search for special categories
  - Call TFT Feature search for feature_request
  - Generate category-specific guidance
  - Store results in evaluation data
- Added `/save_selected_feature` endpoint to store user selections
- Updated `/search_results` route to pass selected features to template

### 3. **templates/search_results.html**
- Added category guidance display section (top of results)
- Added TFT Features section with:
  - Collapsible display showing feature count
  - Checkboxes for feature selection
  - Similarity percentage badges
  - Links to view in ADO
- Added JavaScript for AJAX feature selection

## Configuration Details

### TFT Feature Search
- **Organization**: unifiedactiontracker
- **Project**: Technical Feedback
- **WorkItemType**: Feature
- **Lookback Period**: 12 months
- **Similarity Threshold**: 0.7 (70%)
- **Top Results**: 10 max

### Data Storage
- Selected TFT Feature IDs stored in: `evaluation_data['selected_tft_features']`
- Available for UAT creation process
- Persists for session duration

## Testing

Run test script to verify TFT search:
```bash
python test_tft_search.py
```

## Next Steps for UAT Creation

When creating a UAT work item, check for selected features:
```python
selected_features = evaluation_data.get('selected_tft_features', [])
if selected_features:
    # Add to UAT description or custom field:
    # "Related TFT Features: #123, #456"
```

## UI/UX Details

### Category Guidance Display
- Shown at top of search results
- Color-coded by severity:
  - `warning` (yellow) - technical_support
  - `danger` (red) - cost_billing
  - `info` (blue) - aoai_capacity, capacity
- Formatted with line breaks for readability

### TFT Features Display
- Blue header with count badge
- Each feature shows:
  - Checkbox for selection
  - Title (clickable label)
  - Similarity percentage badge (green)
  - Truncated description
  - Created date and state
  - "View in ADO" button
- Real-time AJAX save on selection
- Visual feedback during save operation

## API Endpoints

### POST /save_selected_feature
**Request:**
```json
{
  "eval_id": "abc123",
  "feature_id": "12345"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feature selected"
}
```

**Notes:**
- Toggles selection (select/deselect)
- Stores in temp_storage for session
- Used by UAT creation process

## Authentication

TFT Feature search uses same authentication as main ADO integration:
- Development: Azure CLI credential (`az login`)
- Production: Update to Service Principal (TODO)

## Links Reference

- **CSS Compass**: https://aka.ms/csscompass
- **Reactive Escalation**: http://aka.ms/reactiveescalation
- **GetHelp**: https://aka.ms/GetHelp
- **AI Capacity Hub**: https://aka.ms/aicapacityhub
- **Capacity Process**: [SharePoint PowerPoint Link]
