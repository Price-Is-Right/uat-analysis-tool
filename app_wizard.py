"""
Wizard Routes for Issue Tracker
Refactored wizard functionality using the new wizard module structure
"""
from flask import Blueprint, request, redirect, url_for, session, flash
from wizard.wizard_controller import wizard_controller

# Create wizard blueprint
wizard_bp = Blueprint('wizard', __name__, url_prefix='/wizard', template_folder='wizard/templates')


@wizard_bp.route('/start')
def wizard_start():
    """Start the wizard process"""
    # Clear any existing wizard data and initialize fresh
    wizard_controller.reset_wizard()
    from wizard.wizard_utils import initialize_wizard_data, save_wizard_data
    save_wizard_data(initialize_wizard_data())
    return redirect(url_for('wizard.wizard_step', step=1))


@wizard_bp.route('/step/<int:step>')
def wizard_step(step):
    """Display wizard step"""
    return wizard_controller.render_step(step)


@wizard_bp.route('/save_step', methods=['POST'])
def wizard_save_step():
    """Save current wizard step data"""
    return wizard_controller.process_step()


@wizard_bp.route('/update_review', methods=['POST'])
def wizard_update_review():
    """Update data from review page"""
    from wizard.step5 import process_step5_update
    return process_step5_update()


@wizard_bp.route('/submit', methods=['POST'])
def wizard_submit():
    """Handle final wizard submission"""
    try:
        # Get the final wizard data
        wizard_data = wizard_controller.process_final_submit()
        
        if not wizard_data:
            flash('Error processing wizard data. Please try again.', 'error')
            return redirect(url_for('wizard_step', step=5))
        
        # Store wizard data for main app submission processing
        session['submission_data'] = {
            'title': wizard_data.get('title', ''),
            'description': wizard_data.get('description', ''),
            'impact': wizard_data.get('impact', ''),
            'opportunity_id': wizard_data.get('opportunity_id', ''),
            'milestone_id': wizard_data.get('milestone_id', ''),
            'source': 'wizard'
        }
        
        # Clear wizard data since we're done with it
        wizard_controller.reset_wizard()
        
        # Redirect to main app submission handler
        return redirect(url_for('submit_issue'))
        
    except Exception as e:
        flash(f'Error during submission: {str(e)}', 'error')
        return redirect(url_for('wizard_step', step=5))


@wizard_bp.route('/reset')
def wizard_reset():
    """Reset the wizard to initial state"""
    return wizard_controller.reset_wizard()


# Additional utility routes for wizard management

@wizard_bp.route('/info/<int:step>')
def wizard_step_info(step):
    """Get information about a specific wizard step (API endpoint)"""
    from flask import jsonify
    info = wizard_controller.get_step_info(step)
    return jsonify(info)


@wizard_bp.route('/progress')
def wizard_progress():
    """Get current wizard progress (API endpoint)"""
    from flask import jsonify
    from wizard.wizard_utils import get_wizard_data, get_step_progress
    
    wizard_data = get_wizard_data()
    current_step = wizard_data.get('step', 1)
    progress = get_step_progress(current_step)
    
    return jsonify({
        'current_step': current_step,
        'progress_percentage': progress,
        'total_steps': 5,
        'is_complete': current_step >= 5
    })