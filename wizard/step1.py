"""
Wizard Step 1: Issue Title
Handles the title collection step of the issue tracker wizard
"""
from flask import request, redirect, url_for, render_template
from .wizard_utils import (
    get_wizard_data, save_wizard_data, validate_required_field, 
    handle_step_validation_error, get_next_step
)


def render_step1():
    """Render the Step 1 template"""
    wizard_data = get_wizard_data()
    wizard_data['step'] = 1
    save_wizard_data(wizard_data)
    return render_template('wizard_step1.html', wizard_data=wizard_data)


def process_step1():
    """Process Step 1 form submission"""
    wizard_data = get_wizard_data()
    
    # Get and validate title
    title = request.form.get('title', '').strip()
    if not validate_required_field(title, 'a title for your issue', 1):
        return handle_step_validation_error(1)
    
    # Save data and proceed
    wizard_data['title'] = title
    wizard_data['step'] = 1
    save_wizard_data(wizard_data)
    
    return redirect(url_for('wizard.wizard_step', step=get_next_step(1)))


def get_step1_validation_rules():
    """Get validation rules for Step 1"""
    return {
        'title': {
            'required': True,
            'max_length': 125,
            'min_length': 5
        }
    }


def get_step1_help_text():
    """Get help text for Step 1"""
    return {
        'title': 'Choose a clear, descriptive title that summarizes your problem in a few words.',
        'examples': [
            'Cannot access email on mobile device',
            'Application crashes when uploading files',
            'Unable to connect to company VPN'
        ]
    }