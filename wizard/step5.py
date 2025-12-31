"""
Wizard Step 5: Review & Submit
Handles the final review and submission step of the issue tracker wizard
"""
from flask import request, redirect, url_for, render_template, flash
from .wizard_utils import (
    get_wizard_data, save_wizard_data, validate_required_field, 
    handle_step_validation_error, clear_wizard_data
)


def render_step5():
    """Render the Step 5 (Review) template"""
    wizard_data = get_wizard_data()
    wizard_data['step'] = 5
    save_wizard_data(wizard_data)
    return render_template('wizard_review.html', wizard_data=wizard_data)


def process_step5_update():
    """Process Step 5 update form submission (when user edits data)"""
    wizard_data = get_wizard_data()
    
    # Update all fields from the form
    wizard_data['title'] = request.form.get('title', '').strip()
    wizard_data['description'] = request.form.get('description', '').strip()
    wizard_data['impact'] = request.form.get('impact', '').strip()
    wizard_data['opportunity_id'] = request.form.get('opportunity_id', '').strip()
    wizard_data['milestone_id'] = request.form.get('milestone_id', '').strip()
    
    # Validate essential fields (IDs are optional)
    validation_errors = validate_step5_data(wizard_data)
    if validation_errors:
        for error in validation_errors:
            flash(error, 'error')
        return handle_step_validation_error(5)
    
    # Save updated data
    save_wizard_data(wizard_data)
    flash('Your information has been updated successfully.', 'success')
    
    return redirect(url_for('wizard.wizard_step', step=5))


def process_step5_submit():
    """Process Step 5 final submission"""
    wizard_data = get_wizard_data()
    
    # Final validation before submission
    validation_errors = validate_step5_data(wizard_data)
    if validation_errors:
        for error in validation_errors:
            flash(error, 'error')
        return handle_step_validation_error(5)
    
    # Return the wizard data for final processing by the main app
    return wizard_data


def validate_step5_data(wizard_data):
    """Validate all wizard data for final submission"""
    errors = []
    
    # Required fields validation
    if not wizard_data.get('title', '').strip():
        errors.append('Title is required.')
    
    if not wizard_data.get('description', '').strip():
        errors.append('Description is required.')
    
    if not wizard_data.get('impact', '').strip():
        errors.append('Impact assessment is required.')
    
    # Optional field length validation
    title = wizard_data.get('title', '')
    if title and len(title) > 125:
        errors.append('Title must be 125 characters or less.')
    
    if title and len(title) < 5:
        errors.append('Title must be at least 5 characters long.')
    
    description = wizard_data.get('description', '')
    if description and len(description) < 20:
        errors.append('Description must be at least 20 characters long.')
    
    impact = wizard_data.get('impact', '')
    if impact and len(impact) < 10:
        errors.append('Impact assessment must be at least 10 characters long.')
    
    return errors


def get_review_summary(wizard_data):
    """Generate a summary of wizard data for review"""
    summary = {
        'total_characters': (
            len(wizard_data.get('title', '')) +
            len(wizard_data.get('description', '')) +
            len(wizard_data.get('impact', ''))
        ),
        'has_msx_info': bool(
            wizard_data.get('opportunity_id', '').strip() or 
            wizard_data.get('milestone_id', '').strip()
        ),
        'completeness_score': calculate_completeness_score(wizard_data)
    }
    
    return summary


def calculate_completeness_score(wizard_data):
    """Calculate how complete the wizard data is (0-100)"""
    score = 0
    
    # Required fields (60% of score)
    if wizard_data.get('title', '').strip():
        score += 20
    if wizard_data.get('description', '').strip():
        score += 20
    if wizard_data.get('impact', '').strip():
        score += 20
    
    # Quality indicators (30% of score)
    title_length = len(wizard_data.get('title', ''))
    if title_length >= 10:
        score += 10
    
    description_length = len(wizard_data.get('description', ''))
    if description_length >= 100:
        score += 10
    elif description_length >= 50:
        score += 5
    
    impact_length = len(wizard_data.get('impact', ''))
    if impact_length >= 50:
        score += 10
    elif impact_length >= 25:
        score += 5
    
    # MSX information (10% of score)
    if wizard_data.get('opportunity_id', '').strip() and wizard_data.get('milestone_id', '').strip():
        score += 10
    elif wizard_data.get('opportunity_id', '').strip() or wizard_data.get('milestone_id', '').strip():
        score += 5
    
    return min(score, 100)


def get_step5_help_text():
    """Get help text for Step 5"""
    return {
        'review': 'Please review all your information before submitting.',
        'edit_instructions': 'You can edit any field directly on this page and click "Update Information" to save changes.',
        'submit_notice': 'Once submitted, we\'ll search for similar issues and provide solutions.',
        'data_retention': 'Your data will be securely stored and used only for issue resolution.'
    }