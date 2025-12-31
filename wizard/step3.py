"""
Wizard Step 3: Impact Assessment
Handles the impact assessment step of the issue tracker wizard
"""
from flask import request, redirect, url_for, render_template
from .wizard_utils import (
    get_wizard_data, save_wizard_data, validate_required_field, 
    handle_step_validation_error, get_next_step
)


def render_step3():
    """Render the Step 3 template"""
    wizard_data = get_wizard_data()
    wizard_data['step'] = 3
    save_wizard_data(wizard_data)
    return render_template('wizard_step3.html', wizard_data=wizard_data)


def process_step3():
    """Process Step 3 form submission"""
    wizard_data = get_wizard_data()
    
    # Get and validate impact
    impact = request.form.get('impact', '').strip()
    if not validate_required_field(impact, 'the impact of this issue', 3):
        return handle_step_validation_error(3, 'Please describe the impact of this issue.')
    
    # Save data and proceed
    wizard_data['impact'] = impact
    wizard_data['step'] = 3
    save_wizard_data(wizard_data)
    
    return redirect(url_for('wizard.wizard_step', step=get_next_step(3)))


def get_step3_validation_rules():
    """Get validation rules for Step 3"""
    return {
        'impact': {
            'required': True,
            'min_length': 10,
            'recommended_length': 50
        }
    }


def get_step3_help_text():
    """Get help text for Step 3"""
    return {
        'impact': 'Describe how this issue affects your customer.',
        'consider_impact_on': [
            'Customer experience',
            'Business Impact'
        ],
        'urgency_indicators': [
            'Critical systems down',
            'Multiple users affected',
            'Approaching deadlines',
            'Revenue impact'
        ],
        'placeholder': '''Describe the impact of this issue:

• How many people are affected?
• Is work blocked or just slowed down?
• Are customers or external users impacted?
• Is there a deadline or time sensitivity?
• Are there financial or business implications?'''
    }


def analyze_impact_urgency(impact_text):
    """Analyze impact text for urgency keywords"""
    if not impact_text:
        return {'is_urgent': False, 'urgency_level': 'low'}
    
    impact_lower = impact_text.lower()
    
    # Define urgency keywords
    critical_keywords = ['critical', 'down', 'stopped', 'blocked', 'urgent']
    high_keywords = ['customer', 'revenue', 'deadline', 'multiple users', 'business impact']
    medium_keywords = ['slow', 'delayed', 'difficulty', 'problem']
    
    # Check for keywords
    has_critical = any(keyword in impact_lower for keyword in critical_keywords)
    has_high = any(keyword in impact_lower for keyword in high_keywords)
    has_medium = any(keyword in impact_lower for keyword in medium_keywords)
    
    if has_critical:
        return {'is_urgent': True, 'urgency_level': 'critical'}
    elif has_high:
        return {'is_urgent': True, 'urgency_level': 'high'}
    elif has_medium:
        return {'is_urgent': False, 'urgency_level': 'medium'}
    else:
        return {'is_urgent': False, 'urgency_level': 'low'}