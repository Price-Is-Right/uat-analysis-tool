"""
Wizard Step 2: Issue Description
Handles the detailed description collection step of the issue tracker wizard
"""
from flask import request, redirect, url_for, render_template
from .wizard_utils import (
    get_wizard_data, save_wizard_data, validate_required_field, 
    handle_step_validation_error, get_next_step
)


def render_step2():
    """Render the Step 2 template"""
    wizard_data = get_wizard_data()
    wizard_data['step'] = 2
    save_wizard_data(wizard_data)
    return render_template('wizard_step2.html', wizard_data=wizard_data)


def process_step2():
    """Process Step 2 form submission"""
    wizard_data = get_wizard_data()
    
    # Get and validate description
    description = request.form.get('description', '').strip()
    if not validate_required_field(description, 'a description of your issue', 2):
        return handle_step_validation_error(2)
    
    # Save data and proceed
    wizard_data['description'] = description
    wizard_data['step'] = 2
    save_wizard_data(wizard_data)
    
    return redirect(url_for('wizard.wizard_step', step=get_next_step(2)))


def get_step2_validation_rules():
    """Get validation rules for Step 2"""
    return {
        'description': {
            'required': True,
            'min_length': 20,
            'recommended_length': 100
        }
    }


def get_step2_help_text():
    """Get help text for Step 2"""
    return {
        'description': 'Include what you\'re trying to do, what\'s happening instead, and desired outcome.',
        'good_details': [
            'What you\'re trying to do',
            'Exact error messages',
            'When it started',
            'What you\'ve already tried'
        ],
        'placeholder': '''Please provide detailed information including:

• What you are trying to do that you cannot?
• What exactly is happening (include any error messages)?
• When did this start happening?
• Have you tried any workarounds or solutions?'''
    }