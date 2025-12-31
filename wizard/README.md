# Wizard Module Documentation

## Overview

The wizard module contains the refactored wizard functionality for the Issue Tracker System. This modular approach separates concerns and makes the code easier to maintain, test, and enhance.

## Structure

```
wizard/
├── __init__.py              # Module initialization
├── wizard_utils.py          # Common utilities and helper functions
├── wizard_controller.py     # Main wizard controller class
├── step1.py                 # Step 1: Issue Title logic
├── step2.py                 # Step 2: Issue Description logic  
├── step3.py                 # Step 3: Impact Assessment logic
├── step4.py                 # Step 4: MSX Information logic
├── step5.py                 # Step 5: Review & Submit logic
└── templates/               # Wizard-specific templates
    ├── wizard_step1.html    # Step 1 template
    ├── wizard_step2.html    # Step 2 template
    ├── wizard_step3.html    # Step 3 template
    ├── wizard_step4.html    # Step 4 template
    └── wizard_review.html   # Step 5 (Review) template
```

## Key Components

### WizardController (wizard_controller.py)

The main controller class that orchestrates all wizard functionality:
- Routes step rendering to appropriate step modules
- Handles step processing and validation
- Manages wizard state and navigation
- Provides step information and metadata

### Step Modules (step1.py - step5.py)

Each step module contains:
- `render_step()`: Renders the step template with current data
- `process_step()`: Processes form submission and validation
- `get_validation_rules()`: Returns validation rules for the step
- `get_help_text()`: Returns help text and guidance for users

### Wizard Utilities (wizard_utils.py)

Common functions used across all steps:
- Session management (get/save wizard data)
- Validation helpers
- Progress calculation
- Step navigation helpers
- Data initialization and cleanup

## Integration with Main App

The wizard module is integrated as a Flask Blueprint in `app_wizard.py`:

```python
from wizard.wizard_controller import wizard_controller

# Routes are registered under /wizard/ prefix
@wizard_bp.route('/step/<int:step>')
def wizard_step(step):
    return wizard_controller.render_step(step)
```

## Benefits of This Structure

### 1. **Separation of Concerns**
- Each step has its own module with dedicated logic
- Templates are organized in a dedicated wizard directory
- Common functionality is centralized in utilities

### 2. **Easy Maintenance**
- Individual step logic can be modified without affecting others
- Adding new steps is straightforward
- Bug fixes are isolated to specific components

### 3. **Enhanced Testing**
- Each step module can be unit tested independently
- Validation logic is easily testable
- Controller orchestration can be tested separately

### 4. **Better Code Organization**
- Related functionality is grouped together
- Clear naming conventions and structure
- Reduced coupling between components

### 5. **Scalability**
- Easy to add new validation rules per step
- Simple to extend with additional features
- Clean integration points for new functionality

## Usage Examples

### Adding a New Validation Rule

```python
# In step1.py
def get_step1_validation_rules():
    return {
        'title': {
            'required': True,
            'max_length': 125,
            'min_length': 5,
            'pattern': r'^[a-zA-Z0-9\s\-_\.]+$'  # New pattern rule
        }
    }
```

### Adding Custom Step Logic

```python
# In step3.py
def analyze_impact_urgency(impact_text):
    # Custom business logic for impact analysis
    urgency_keywords = ['critical', 'urgent', 'blocked']
    if any(keyword in impact_text.lower() for keyword in urgency_keywords):
        return {'urgency_level': 'high', 'requires_escalation': True}
    return {'urgency_level': 'normal', 'requires_escalation': False}
```

### Extending the Controller

```python
# In wizard_controller.py
def export_wizard_data(self, format='json'):
    """Export current wizard data in specified format"""
    wizard_data = get_wizard_data()
    if format == 'json':
        return json.dumps(wizard_data, indent=2)
    elif format == 'csv':
        # CSV export logic
        pass
```

## Migration from Old Structure

The refactoring maintains backward compatibility while providing the new modular structure:

1. **Old Routes**: Still work through the legacy path handling in submit_issue()
2. **New Routes**: Use the blueprint structure for cleaner organization
3. **Templates**: Moved to wizard/templates/ but maintain same functionality
4. **Session Data**: Compatible between old and new systems

## Future Enhancements

With this modular structure, future enhancements become easier:

1. **Multi-language Support**: Add localization per step
2. **Dynamic Steps**: Add/remove steps based on user input
3. **Step Dependencies**: Complex validation across multiple steps
4. **Progress Persistence**: Save progress to database instead of session
5. **Step Analytics**: Track user behavior per step for optimization

## Troubleshooting

### Common Issues

1. **Template Not Found**: Ensure templates are in `wizard/templates/` directory
2. **Route Errors**: Check blueprint route names use `wizard.` prefix
3. **Import Errors**: Verify all wizard modules are properly imported
4. **Session Issues**: Check that wizard utilities are properly managing session data

### Debug Mode

Enable debug mode for detailed error information:

```python
# In app.py or app_wizard.py
app.debug = True
```

This will provide detailed stack traces for any wizard-related errors.