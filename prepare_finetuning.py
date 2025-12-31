"""
Fine-Tuning Preparation Script
Converts corrections.json to OpenAI fine-tuning format
Prepares training data for custom model fine-tuning
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime

from ai_config import get_config


class FineTuningPreparation:
    """
    Prepares fine-tuning data from user corrections
    
    Features:
    - Converts corrections to OpenAI format
    - Creates train/validation split
    - Generates system prompts
    - Validates data quality
    """
    
    def __init__(self):
        self.config = get_config()
        self.ft_config = self.config.fine_tuning
        
        print(f"[FineTuning] Initialized")
        print(f"[FineTuning] Corrections file: {self.ft_config.corrections_file}")
        print(f"[FineTuning] Output directory: {self.ft_config.training_output_dir}")
    
    def load_corrections(self) -> List[Dict[str, Any]]:
        """Load corrections from JSON file"""
        if not os.path.exists(self.ft_config.corrections_file):
            raise FileNotFoundError(f"Corrections file not found: {self.ft_config.corrections_file}")
        
        with open(self.ft_config.corrections_file, 'r', encoding='utf-8') as f:
            corrections = json.load(f)
        
        print(f"[FineTuning] Loaded {len(corrections)} corrections")
        return corrections
    
    def _build_system_message(self) -> str:
        """Build system message for fine-tuning"""
        # Use same categories/intents as LLMClassifier
        from llm_classifier import LLMClassifier
        
        categories = LLMClassifier.VALID_CATEGORIES
        intents = LLMClassifier.VALID_INTENTS
        business_impacts = LLMClassifier.VALID_BUSINESS_IMPACTS
        
        return f"""You are an expert Azure support ticket classifier trained on real customer feedback.

You must classify each inquiry into ONE category and ONE intent:

CATEGORIES: {', '.join(categories)}
INTENTS: {', '.join(intents)}
BUSINESS IMPACT: {', '.join(business_impacts)}

CLASSIFICATION RULES (learned from corrections):
1. Context is critical - understand WHY the customer is asking, not just WHAT they mention
2. Technical problems take priority - errors, failures, "not working" indicate technical_support
3. Distinguish product names from inquiries - mentioning a product ≠ asking about its roadmap
4. Migration context - "roadmap" in migration plan ≠ product roadmap inquiry
5. Regional availability - "required in <region>" indicates service_availability + regional_availability
6. Timeline requests - "when will", "ETA", "release date" indicate roadmap_inquiry
7. Seeking guidance - demos, comparisons, architecture advice = seeking_guidance

Respond with valid JSON only:
{{
    "category": "<category>",
    "intent": "<intent>",
    "business_impact": "<impact>",
    "confidence": <0.0-1.0>,
    "reasoning": "<explanation>"
}}"""
    
    def _convert_correction_to_training_example(self, correction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a correction to OpenAI fine-tuning format
        
        Format:
        {
            "messages": [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
        """
        # Extract original and corrected data
        original = correction.get("original", {})
        corrected = correction.get("corrected", {})
        reasoning = correction.get("reasoning", "Corrected based on user feedback")
        
        # Build user message
        title = original.get("title", "")
        description = original.get("description", "")
        impact = original.get("impact", "")
        
        user_content = f"""**Title:** {title}
**Description:** {description}
**Stated Impact:** {impact}

Classify this inquiry:"""
        
        # Build assistant response (the correct answer)
        assistant_response = {
            "category": corrected.get("category", ""),
            "intent": corrected.get("intent", ""),
            "business_impact": corrected.get("business_impact", "medium"),
            "confidence": 1.0,  # User corrections are authoritative
            "reasoning": reasoning
        }
        
        return {
            "messages": [
                {"role": "system", "content": self._build_system_message()},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": json.dumps(assistant_response)}
            ]
        }
    
    def prepare_training_data(self) -> Dict[str, Any]:
        """
        Prepare training data from corrections
        
        Returns:
            Dictionary with train/validation datasets and metadata
        """
        corrections = self.load_corrections()
        
        if not corrections:
            print("[FineTuning] No corrections available")
            return {
                "train": [],
                "validation": [],
                "metadata": {
                    "total_examples": 0,
                    "train_count": 0,
                    "validation_count": 0
                }
            }
        
        # Convert to training examples
        examples = []
        for correction in corrections:
            try:
                example = self._convert_correction_to_training_example(correction)
                examples.append(example)
            except Exception as e:
                print(f"[FineTuning] Error converting correction: {e}")
                continue
        
        print(f"[FineTuning] Converted {len(examples)} corrections to training examples")
        
        # Split into train/validation
        validation_split = self.ft_config.validation_split
        validation_count = int(len(examples) * validation_split)
        
        # Shuffle examples (deterministic for reproducibility)
        import random
        random.seed(42)
        random.shuffle(examples)
        
        validation_data = examples[:validation_count]
        train_data = examples[validation_count:]
        
        print(f"[FineTuning] Split: {len(train_data)} train, {len(validation_data)} validation")
        
        return {
            "train": train_data,
            "validation": validation_data,
            "metadata": {
                "total_examples": len(examples),
                "train_count": len(train_data),
                "validation_count": len(validation_data),
                "created_at": datetime.now().isoformat(),
                "config": {
                    "n_epochs": self.ft_config.n_epochs,
                    "batch_size": self.ft_config.batch_size,
                    "learning_rate_multiplier": self.ft_config.learning_rate_multiplier
                }
            }
        }
    
    def save_training_files(self, training_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Save training data to JSONL files
        
        Returns:
            Dictionary with file paths
        """
        os.makedirs(self.ft_config.training_output_dir, exist_ok=True)
        
        output_files = {}
        
        # Save training data
        train_file = os.path.join(self.ft_config.training_output_dir, "train.jsonl")
        with open(train_file, 'w', encoding='utf-8') as f:
            for example in training_data["train"]:
                f.write(json.dumps(example) + '\n')
        output_files["train"] = train_file
        print(f"[FineTuning] Saved training data to: {train_file}")
        
        # Save validation data
        if training_data["validation"]:
            val_file = os.path.join(self.ft_config.training_output_dir, "validation.jsonl")
            with open(val_file, 'w', encoding='utf-8') as f:
                for example in training_data["validation"]:
                    f.write(json.dumps(example) + '\n')
            output_files["validation"] = val_file
            print(f"[FineTuning] Saved validation data to: {val_file}")
        
        # Save metadata
        metadata_file = os.path.join(self.ft_config.training_output_dir, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(training_data["metadata"], f, indent=2)
        output_files["metadata"] = metadata_file
        print(f"[FineTuning] Saved metadata to: {metadata_file}")
        
        return output_files
    
    def generate_fine_tuning_instructions(self, file_paths: Dict[str, str]) -> str:
        """Generate instructions for fine-tuning with OpenAI"""
        
        instructions = f"""
# Fine-Tuning Instructions

## Files Generated
- Training data: {file_paths.get('train', 'N/A')}
- Validation data: {file_paths.get('validation', 'N/A')}
- Metadata: {file_paths.get('metadata', 'N/A')}

## Fine-Tuning with Azure OpenAI

### 1. Upload Training Files

```bash
# Upload training file
az cognitiveservices account deployment create \\
  --name <your-openai-resource> \\
  --resource-group <your-resource-group> \\
  --deployment-name <deployment-name> \\
  --model-name gpt-4o \\
  --model-version <version> \\
  --sku-capacity 1 \\
  --sku-name Standard

# Or use Azure OpenAI Studio:
# 1. Go to Azure OpenAI Studio
# 2. Navigate to "Fine-tuning"
# 3. Click "Create fine-tuning job"
# 4. Upload train.jsonl and validation.jsonl
```

### 2. Create Fine-Tuning Job

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview"
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file="<uploaded-file-id>",
    validation_file="<uploaded-validation-file-id>",
    model="gpt-4o",
    hyperparameters={{
        "n_epochs": {self.ft_config.n_epochs},
        "batch_size": {self.ft_config.batch_size},
        "learning_rate_multiplier": {self.ft_config.learning_rate_multiplier}
    }}
)

print(f"Fine-tuning job created: {{job.id}}")
```

### 3. Monitor Job Status

```python
# Check job status
status = client.fine_tuning.jobs.retrieve(job.id)
print(f"Status: {{status.status}}")

# List events
events = client.fine_tuning.jobs.list_events(job.id)
for event in events:
    print(event)
```

### 4. Use Fine-Tuned Model

Once training completes, update your configuration:

```python
# In ai_config.py or environment variables
AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT = "<fine-tuned-model-name>"
```

## Expected Improvements

- Better context understanding
- Reduced misclassifications
- More accurate confidence scores
- Improved reasoning quality

## Cost Estimation

Fine-tuning cost depends on:
- Training file size: ~{len(file_paths.get('train', ''))} examples
- Model: GPT-4o
- Epochs: {self.ft_config.n_epochs}

Estimated cost: Check Azure OpenAI pricing for fine-tuning rates.

## Next Steps

1. Review training/validation files
2. Upload files to Azure OpenAI
3. Create fine-tuning job
4. Monitor training progress
5. Test fine-tuned model
6. Update deployment configuration
7. Compare accuracy vs. base model
"""
        
        return instructions


def main():
    """Main function to prepare fine-tuning data"""
    print("Fine-Tuning Data Preparation")
    print("=" * 50)
    
    try:
        prep = FineTuningPreparation()
        
        # Prepare training data
        print("\nPreparing training data from corrections...")
        training_data = prep.prepare_training_data()
        
        if training_data["metadata"]["total_examples"] == 0:
            print("\n⚠️  No corrections available for fine-tuning")
            print("Add corrections through the UAT Analysis Tool to build training data")
            return
        
        # Save training files
        print("\nSaving training files...")
        file_paths = prep.save_training_files(training_data)
        
        # Generate instructions
        instructions = prep.generate_fine_tuning_instructions(file_paths)
        
        # Save instructions
        instructions_file = os.path.join(
            prep.ft_config.training_output_dir,
            "FINE_TUNING_INSTRUCTIONS.md"
        )
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"\n✓ Fine-tuning preparation complete!")
        print(f"\nFiles created:")
        for key, path in file_paths.items():
            print(f"  - {key}: {path}")
        print(f"  - instructions: {instructions_file}")
        
        print(f"\n📊 Summary:")
        print(f"  Total examples: {training_data['metadata']['total_examples']}")
        print(f"  Training: {training_data['metadata']['train_count']}")
        print(f"  Validation: {training_data['metadata']['validation_count']}")
        
        print(f"\nNext: Review {instructions_file} for fine-tuning steps")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
