"""
Wizard Controller
Main controller for the Issue Tracker Wizard
"""
from flask import request, redirect, url_for
from .wizard_utils import validate_wizard_step, clear_wizard_data
from .step1 import render_step1, process_step1
from .step2 import render_step2, process_step2
from .step3 import render_step3, process_step3
from .step4 import render_step4, process_step4
from .step5 import render_step5, process_step5_update, process_step5_submit


class WizardController:
    """Main wizard controller class"""
    
    def __init__(self):
        self.step_renderers = {
            1: render_step1,
            2: render_step2,
            3: render_step3,
            4: render_step4,
            5: render_step5
        }
        
        self.step_processors = {
            1: process_step1,
            2: process_step2,
            3: process_step3,
            4: process_step4,
            5: process_step5_update  # Default to update for step 5
        }
    
    def render_step(self, step):
        """Render a specific wizard step"""
        if not validate_wizard_step(step):
            return redirect(url_for('index'))
        
        renderer = self.step_renderers.get(step)
        if renderer:
            return renderer()
        else:
            return redirect(url_for('index'))
    
    def process_step(self, step=None):
        """Process wizard step form submission"""
        # If no step provided, determine from wizard data
        if step is None:
            from .wizard_utils import get_wizard_data
            wizard_data = get_wizard_data()
            step = wizard_data.get('step', 1)
        
        if not validate_wizard_step(step):
            return redirect(url_for('index'))
        
        processor = self.step_processors.get(step)
        if processor:
            return processor()
        else:
            return redirect(url_for('index'))
    
    def process_final_submit(self):
        """Process final wizard submission"""
        return process_step5_submit()
    
    def reset_wizard(self):
        """Reset the wizard to initial state"""
        clear_wizard_data()
        return redirect(url_for('index'))
    
    def get_step_info(self, step):
        """Get information about a specific step"""
        step_info = {
            1: {
                'title': 'Issue Title',
                'description': 'What would be a good title for this issue?',
                'icon': 'fas fa-edit'
            },
            2: {
                'title': 'Issue Description',
                'description': 'Can you describe the issue in as much detail as possible?',
                'icon': 'fas fa-align-left'
            },
            3: {
                'title': 'Impact Assessment',
                'description': 'To help engineering prioritize this issue, what would be the impact to the customer?',
                'icon': 'fas fa-exclamation-triangle'
            },
            4: {
                'title': 'MSX Information',
                'description': 'Please provide opportunity information',
                'icon': 'fas fa-hashtag'
            },
            5: {
                'title': 'Review & Submit',
                'description': 'Please review and submit your issue',
                'icon': 'fas fa-check-circle'
            }
        }
        
        return step_info.get(step, {
            'title': 'Unknown Step',
            'description': 'Invalid step',
            'icon': 'fas fa-question'
        })


# Global wizard controller instance
wizard_controller = WizardController()