# Corrections System Implementation Plan

## Current State Assessment

### ✅ What's Working

1. **Data Collection**
   - `corrections.json` created and structured
   - App.py saves user corrections via feedback UI
   - Format: original text + category + corrected category

2. **Pattern Matcher Integration**
   - Loads corrections.json on startup
   - Searches for similar text patterns
   - Applies confidence boost if match found
   - Tracks corrections in reasoning output

3. **User Interface**
   - Feedback form captures corrections
   - Stores in evaluation tracker
   - Saves to corrections.json

### ❌ What's NOT Working

1. **Hybrid Analyzer Integration**
   - Corrections not extracted as features
   - Not passed to LLM classifier
   - AI never sees correction data

2. **Fine-tuning Pipeline**
   - No GPT-4o fine-tuning implemented
   - No training data preparation
   - No model deployment automation

3. **Correction Quality**
   - No validation of corrections
   - No correction confidence scoring
   - No duplicate detection

---

## Implementation Phases

### Phase 1: Pass Corrections to AI (Quick Win)

**Goal:** Make LLM aware of corrections without fine-tuning

**Steps:**

1. **Update Feature Extraction** (`hybrid_context_analyzer.py`)
   ```python
   def _extract_pattern_features(self, pattern_result: Any) -> Dict[str, Any]:
       features = {
           "category_scores": {...},
           "detected_products": [...],
           "technical_indicators": [...],
           # NEW: Add corrections
           "relevant_corrections": self._find_relevant_corrections(pattern_result)
       }
       return features
   
   def _find_relevant_corrections(self, pattern_result) -> List[Dict]:
       """Find corrections similar to current issue"""
       corrections = []
       for correction in self.corrections_data.get('corrections', []):
           if self._is_similar(pattern_result, correction):
               corrections.append({
                   "original_category": correction['original_category'],
                   "corrected_category": correction['corrected_category'],
                   "reason": correction.get('correction_notes', '')
               })
       return corrections[:3]  # Top 3 most relevant
   ```

2. **Update LLM Prompt** (`llm_classifier.py`)
   ```python
   def classify(self, text: str, pattern_features: Dict = None) -> ClassificationResult:
       # Add corrections to context
       prompt_parts = [
           f"Text to classify: {text}",
           "\nPattern Analysis Context:",
           f"- Detected category: {pattern_features.get('category_scores', {})}",
           f"- Products: {pattern_features.get('detected_products', [])}",
       ]
       
       # NEW: Include corrections
       if pattern_features.get('relevant_corrections'):
           prompt_parts.append("\nPrevious Corrections (Learn from these):")
           for corr in pattern_features['relevant_corrections']:
               prompt_parts.append(
                   f"- Similar issue was misclassified as '{corr['original_category']}' "
                   f"but should be '{corr['corrected_category']}'"
               )
       
       prompt = "\n".join(prompt_parts)
       # ... rest of classification
   ```

3. **Load Corrections in Hybrid Analyzer**
   ```python
   class HybridContextAnalyzer:
       def __init__(self):
           # ... existing initialization
           self.corrections_data = self._load_corrections()
       
       def _load_corrections(self) -> Dict:
           try:
               with open('corrections.json', 'r') as f:
                   return json.load(f)
           except FileNotFoundError:
               return {"corrections": []}
   ```

**Estimated Time:** 2-3 hours  
**Impact:** Medium - AI sees corrections as context  
**Risk:** Low - doesn't change existing logic, just adds context

---

### Phase 2: Correction Quality & Management

**Goal:** Ensure correction data is high quality

**Steps:**

1. **Correction Validation**
   ```python
   def validate_correction(correction: Dict) -> bool:
       """Ensure correction is valid before saving"""
       required_fields = ['original_text', 'original_category', 'corrected_category']
       
       # Check required fields
       if not all(field in correction for field in required_fields):
           return False
       
       # Check categories are valid
       valid_categories = [cat.value for cat in IssueCategory]
       if correction['corrected_category'] not in valid_categories:
           return False
       
       # Check not same category
       if correction['original_category'] == correction['corrected_category']:
           return False
       
       return True
   ```

2. **Duplicate Detection**
   ```python
   def is_duplicate_correction(new_correction: Dict, existing: List[Dict]) -> bool:
       """Check if correction already exists"""
       for corr in existing:
           # Same text and same correction
           if (corr['original_text'].lower() == new_correction['original_text'].lower() and
               corr['corrected_category'] == new_correction['corrected_category']):
               return True
       return False
   ```

3. **Correction Confidence Scoring**
   ```python
   def calculate_correction_confidence(correction: Dict) -> float:
       """Score how reliable this correction is"""
       confidence = 0.5  # Base
       
       # Boost if has detailed notes
       if correction.get('correction_notes'):
           confidence += 0.2
       
       # Boost if same correction appears multiple times
       duplicate_count = count_similar_corrections(correction)
       confidence += min(duplicate_count * 0.1, 0.3)
       
       return min(confidence, 1.0)
   ```

**Estimated Time:** 3-4 hours  
**Impact:** High - improves correction data quality  
**Risk:** Low - only affects data validation

---

### Phase 3: Semantic Similarity Matching

**Goal:** Find relevant corrections using embeddings, not just keyword matching

**Steps:**

1. **Generate Embeddings for Corrections**
   ```python
   class CorrectionIndex:
       def __init__(self, embedding_service: EmbeddingService):
           self.embedding_service = embedding_service
           self.corrections = []
           self.embeddings = []
       
       def index_corrections(self, corrections: List[Dict]):
           """Generate embeddings for all corrections"""
           for correction in corrections:
               text = correction['original_text']
               embedding = self.embedding_service.get_embedding(text)
               self.corrections.append(correction)
               self.embeddings.append(embedding)
       
       def find_similar(self, query_text: str, top_k: int = 3) -> List[Dict]:
           """Find most similar corrections using cosine similarity"""
           query_embedding = self.embedding_service.get_embedding(query_text)
           
           similarities = []
           for i, corr_embedding in enumerate(self.embeddings):
               similarity = cosine_similarity(query_embedding, corr_embedding)
               similarities.append((similarity, self.corrections[i]))
           
           # Sort by similarity, return top K
           similarities.sort(reverse=True, key=lambda x: x[0])
           return [corr for sim, corr in similarities[:top_k] if sim > 0.75]
   ```

2. **Update Hybrid Analyzer**
   ```python
   class HybridContextAnalyzer:
       def __init__(self):
           # ... existing init
           self.correction_index = CorrectionIndex(self.embedding_service)
           self._index_corrections()
       
       def _index_corrections(self):
           """Build correction index at startup"""
           corrections = self.corrections_data.get('corrections', [])
           if corrections:
               self.correction_index.index_corrections(corrections)
               print(f"✅ Indexed {len(corrections)} corrections for similarity search")
       
       def _find_relevant_corrections(self, text: str) -> List[Dict]:
           """Find semantically similar corrections"""
           return self.correction_index.find_similar(text, top_k=3)
   ```

**Estimated Time:** 4-5 hours  
**Impact:** High - much better correction matching  
**Risk:** Medium - adds embeddings overhead

---

### Phase 4: Fine-tuning Pipeline (Advanced)

**Goal:** Actually fine-tune GPT-4o on corrections

**Steps:**

1. **Prepare Training Data**
   ```python
   def prepare_fine_tuning_dataset(corrections: List[Dict]) -> List[Dict]:
       """Convert corrections to OpenAI fine-tuning format"""
       training_data = []
       
       for correction in corrections:
           # Format: {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
           example = {
               "messages": [
                   {
                       "role": "system",
                       "content": "You are an IT support issue classifier..."
                   },
                   {
                       "role": "user",
                       "content": f"Classify this issue: {correction['original_text']}"
                   },
                   {
                       "role": "assistant",
                       "content": json.dumps({
                           "category": correction['corrected_category'],
                           "intent": correction['corrected_intent'],
                           "reasoning": correction.get('correction_notes', '')
                       })
                   }
               ]
           }
           training_data.append(example)
       
       return training_data
   ```

2. **Upload Training File**
   ```python
   from openai import AzureOpenAI
   
   def upload_training_data(client: AzureOpenAI, training_data: List[Dict]):
       """Upload training data to Azure OpenAI"""
       # Save to JSONL
       with open('fine_tuning_data.jsonl', 'w') as f:
           for example in training_data:
               f.write(json.dumps(example) + '\n')
       
       # Upload file
       with open('fine_tuning_data.jsonl', 'rb') as f:
           response = client.files.create(
               file=f,
               purpose='fine-tune'
           )
       
       return response.id
   ```

3. **Create Fine-tuning Job**
   ```python
   def create_fine_tuning_job(client: AzureOpenAI, training_file_id: str):
       """Start fine-tuning job"""
       job = client.fine_tuning.jobs.create(
           training_file=training_file_id,
           model="gpt-4o-2024-08-06",  # Base model
           hyperparameters={
               "n_epochs": 3,
               "batch_size": 4,
               "learning_rate_multiplier": 0.1
           }
       )
       return job.id
   ```

4. **Monitor & Deploy**
   ```python
   def monitor_fine_tuning(client: AzureOpenAI, job_id: str):
       """Check fine-tuning job status"""
       job = client.fine_tuning.jobs.retrieve(job_id)
       print(f"Status: {job.status}")
       
       if job.status == 'succeeded':
           print(f"✅ Fine-tuned model: {job.fine_tuned_model}")
           # Update .env with new deployment
           return job.fine_tuned_model
       
       return None
   ```

**Estimated Time:** 8-10 hours + Azure costs  
**Impact:** Very High - truly learned model  
**Risk:** High - requires Azure OpenAI permissions, costs money

---

## Recommended Implementation Order

### Week 1: Quick Wins
- ✅ **Phase 1** - Pass corrections to AI as context (2-3 hours)
- ✅ **Phase 2** - Correction validation and quality (3-4 hours)

### Week 2: Enhanced Matching  
- ✅ **Phase 3** - Semantic similarity matching (4-5 hours)
- Test with real data, gather more corrections

### Month 2+: Fine-tuning (Optional)
- ⚠️ **Phase 4** - Full fine-tuning pipeline (8-10 hours)
- Requires: 50+ high-quality corrections
- Requires: Budget for Azure OpenAI fine-tuning
- Requires: Permissions to create fine-tuned deployments

---

## Testing Strategy

### Phase 1 Testing
```python
# Test correction context passing
def test_corrections_in_context():
    # Add sample correction
    correction = {
        "original_text": "sql mi in west europe",
        "original_category": "training_documentation",
        "corrected_category": "service_availability"
    }
    save_correction(correction)
    
    # Run similar query
    result = analyzer.analyze_context(
        "SQL Managed Instance availability in West Europe",
        "Is it available?"
    )
    
    # Check AI saw correction
    assert "service_availability" in result.reasoning
    assert result.category == "service_availability"
```

### Phase 2 Testing
```python
# Test validation
def test_correction_validation():
    invalid = {"original_text": "test"}  # Missing fields
    assert not validate_correction(invalid)
    
    same_category = {
        "original_text": "test",
        "original_category": "technical_support",
        "corrected_category": "technical_support"
    }
    assert not validate_correction(same_category)
```

### Phase 3 Testing
```python
# Test semantic matching
def test_semantic_correction_matching():
    # Add correction for "Azure OpenAI capacity"
    correction = {
        "original_text": "need more openai quota",
        "corrected_category": "capacity_request"
    }
    
    # Query with different wording
    similar = find_similar_corrections("require additional gpt-4 capacity")
    
    # Should find the correction
    assert len(similar) > 0
    assert similar[0]['corrected_category'] == "capacity_request"
```

---

## Metrics to Track

### Before Implementation
- Pattern-only accuracy: ~60-70%
- AI accuracy: ~85-95%
- Corrections in database: 0
- AI sees corrections: No

### After Phase 1
- AI sees corrections: Yes
- Correction application rate: Track in logs
- Improved accuracy on corrected patterns: Measure

### After Phase 3
- Semantic match rate: % of relevant corrections found
- Average similarity score: Should be > 0.8
- Correction cache hit rate: Track performance

### After Phase 4 (Fine-tuning)
- Fine-tuned model accuracy: Compare to base model
- Inference cost: Should be same or lower
- Training cost: One-time expense

---

## Cost Analysis

### Phase 1-3: In-Context Learning
- **Cost:** $0 additional (uses existing embeddings/LLM calls)
- **Benefit:** Immediate improvement on known patterns
- **ROI:** High

### Phase 4: Fine-tuning
- **Training Cost:** ~$50-200 (depends on dataset size)
- **Inference Cost:** Same as base GPT-4o
- **Deployment Cost:** Standard Azure hosting
- **Benefit:** Permanent model improvement
- **ROI:** Medium (requires scale to justify)

---

## Decision Matrix

| Approach | Implementation Time | Cost | Improvement | When to Use |
|----------|-------------------|------|-------------|-------------|
| **Phase 1: Context** | 2-3 hours | $0 | +5-10% | Always (quick win) |
| **Phase 2: Quality** | 3-4 hours | $0 | +5% | When you have >10 corrections |
| **Phase 3: Semantic** | 4-5 hours | $0 | +10-15% | When you have >20 corrections |
| **Phase 4: Fine-tune** | 8-10 hours | $100-500 | +15-25% | When you have >50 corrections |

**Recommendation:** Start with Phases 1-2, collect more corrections, then evaluate Phase 3-4.

---

## Next Steps

1. **Immediate (Today):**
   - Test current corrections.json (currently empty)
   - Generate a few test corrections manually
   - Verify they're being loaded by pattern matcher

2. **This Week:**
   - Implement Phase 1 (pass to AI)
   - Implement Phase 2 (validation)
   - Deploy and monitor

3. **Next Month:**
   - Collect 20+ real corrections from users
   - Implement Phase 3 (semantic matching)
   - Measure improvement

4. **Future (3+ months):**
   - If 50+ corrections collected
   - If budget approved
   - Implement Phase 4 (fine-tuning)
