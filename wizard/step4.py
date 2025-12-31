"""
Wizard Step 4: MSX Information
Handles the Opportunity ID and Milestone ID collection step of the issue tracker wizard
"""
from flask import request, redirect, url_for, render_template, flash
from .wizard_utils import (
    get_wizard_data, save_wizard_data, handle_step_validation_error, get_next_step
)


def render_step4():
    """Render the Step 4 template"""
    wizard_data = get_wizard_data()
    wizard_data['step'] = 4
    save_wizard_data(wizard_data)
    return render_template('wizard_step4.html', wizard_data=wizard_data)


def process_step4():
    """Process Step 4 form submission"""
    wizard_data = get_wizard_data()
    
    # Get form data
    opportunity_id = request.form.get('opportunity_id', '').strip()
    milestone_id = request.form.get('milestone_id', '').strip()
    skip_validation = request.form.get('skip_id_validation', '') == 'true'
    
    # Validate IDs if not explicitly skipped
    if not skip_validation:
        validation_result = validate_msx_ids(opportunity_id, milestone_id)
        if not validation_result['is_valid']:
            flash(validation_result['message'], 'error')
            return handle_step_validation_error(4)
    
    # Save data and proceed
    wizard_data['opportunity_id'] = opportunity_id
    wizard_data['milestone_id'] = milestone_id
    wizard_data['step'] = 4
    save_wizard_data(wizard_data)
    
    return redirect(url_for('wizard.wizard_step', step=get_next_step(4)))


def validate_msx_ids(opportunity_id, milestone_id):
    """Validate MSX ID fields"""
    # Check if both fields are empty
    if not opportunity_id and not milestone_id:
        return {
            'is_valid': False,
            'message': 'Please provide both Opportunity ID and Milestone ID, or use the modal to continue without them.',
            'requires_modal': True
        }
    
    # Check if only one field is provided
    if not opportunity_id or not milestone_id:
        return {
            'is_valid': False,
            'message': 'Please provide both Opportunity ID and Milestone ID, or use the modal to continue without them.',
            'requires_modal': True
        }
    
    # Both fields have values
    return {
        'is_valid': True,
        'message': 'MSX information validated successfully.',
        'requires_modal': False
    }


def get_step4_validation_rules():
    """Get validation rules for Step 4"""
    return {
        'opportunity_id': {
            'required': False,
            'pattern': r'^[A-Za-z0-9-_]+$',  # Alphanumeric with hyphens and underscores
            'description': 'Alphanumeric characters, hyphens, and underscores only'
        },
        'milestone_id': {
            'required': False,
            'pattern': r'^[A-Za-z0-9-_]+$',  # Alphanumeric with hyphens and underscores
            'description': 'Alphanumeric characters, hyphens, and underscores only'
        }
    }


def get_step4_help_text():
    """Get help text for Step 4"""
    return {
        'opportunity_id': 'The unique identifier for the MSX opportunity',
        'milestone_id': 'The unique identifier for the MSX milestone',
        'purpose': 'These IDs help us link this issue to the correct opportunity and milestone.',
        'benefits': [
            'Reference the business impact of this issue',
            'Prioritize the issue correctly',
            'Link it to the appropriate business objectives',
            'Communicate status updates to stakeholders'
        ],
        'warning_message': {
            'title': 'Missing Business Impact Information',
            'description': 'Without these identifiers, it will be difficult for engineering to:',
            'consequences': [
                'Reference the business impact of this issue',
                'Prioritize the issue correctly',
                'Link it to the appropriate business objectives',
                'Communicate status updates to stakeholders'
            ]
        }
    }


def check_id_completeness(opportunity_id, milestone_id):
    """Check completeness of ID fields"""
    both_empty = not opportunity_id and not milestone_id
    both_filled = opportunity_id and milestone_id
    partially_filled = bool(opportunity_id) != bool(milestone_id)
    
    return {
        'both_empty': both_empty,
        'both_filled': both_filled,
        'partially_filled': partially_filled,
        'requires_warning': both_empty or partially_filled
    }