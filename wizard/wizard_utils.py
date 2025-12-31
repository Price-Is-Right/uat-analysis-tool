"""
Wizard Utilities Module
Common functionality and utilities for the Issue Tracker Wizard
"""
from flask import session, redirect, url_for, flash, request, render_template


def initialize_wizard_data():
    """Initialize wizard data structure"""
    return {
        'title': '',
        'description': '',
        'impact': '',
        'opportunity_id': '',
        'milestone_id': '',
        'step': 1
    }


def get_wizard_data():
    """Get wizard data from session, initialize if needed"""
    if 'wizard_data' not in session:
        session['wizard_data'] = initialize_wizard_data()
    return session['wizard_data']


def save_wizard_data(wizard_data):
    """Save wizard data to session"""
    session['wizard_data'] = wizard_data


def validate_wizard_step(step):
    """Validate if wizard step is valid"""
    return 1 <= step <= 5


def clear_wizard_data():
    """Clear wizard data from session"""
    if 'wizard_data' in session:
        del session['wizard_data']


def get_step_progress(step):
    """Get progress percentage for a given step"""
    progress_map = {
        1: 20,
        2: 40,
        3: 60,
        4: 80,
        5: 100
    }
    return progress_map.get(step, 0)


def get_step_title(step):
    """Get the title for a given step"""
    titles = {
        1: "Issue Title",
        2: "Issue Description", 
        3: "Impact Assessment",
        4: "MSX Information",
        5: "Review & Submit"
    }
    return titles.get(step, "Unknown Step")


def validate_required_field(field_value, field_name, step):
    """Validate that a required field has a value"""
    if not field_value:
        flash(f'Please provide {field_name}.', 'error')
        return False
    return True


def handle_step_validation_error(step, message=None):
    """Handle validation error for a step"""
    if message:
        flash(message, 'error')
    return redirect(url_for('wizard.wizard_step', step=step))


def get_next_step(current_step):
    """Get the next step number"""
    if current_step < 5:
        return current_step + 1
    return 5  # Stay on review step


def get_previous_step(current_step):
    """Get the previous step number"""
    if current_step > 1:
        return current_step - 1
    return 1  # Stay on first step