"""
Admin Service - Dedicated microservice for administrative functions
Port: 8004
Responsibilities:
- Evaluation data viewer and search
- System configuration (future)
- User management (future)
- Audit logs (future)
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import os
import json
from typing import List, Dict, Any, Optional
from blob_storage_helper import (
    load_context_evaluations, 
    save_context_evaluations, 
    delete_context_evaluation,
    load_corrections,
    save_corrections
)
from keyvault_config import get_keyvault_config

app = Flask(__name__, template_folder='templates/admin')
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize services
kv_config = get_keyvault_config()

# Application Insights Integration
try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.flask.flask_middleware import FlaskMiddleware
    import logging
    
    config = kv_config.get_config()
    app_insights_key = config.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    
    if app_insights_key:
        # Add Azure logging handler
        logger = logging.getLogger(__name__)
        logger.addHandler(AzureLogHandler(connection_string=app_insights_key))
        logger.setLevel(logging.INFO)
        
        # Add request tracking
        middleware = FlaskMiddleware(app, exporter=None)
        
        print("✅ Application Insights telemetry enabled")
        TELEMETRY_ENABLED = True
    else:
        print("⚠️  Application Insights not configured")
        TELEMETRY_ENABLED = False
except ImportError:
    print("⚠️  opencensus-ext-azure not installed - telemetry disabled")
    TELEMETRY_ENABLED = False
except Exception as e:
    print(f"⚠️  Application Insights setup failed: {e}")
    TELEMETRY_ENABLED = False

# TODO: Add authentication middleware here
# @app.before_request
# def check_authentication():
#     if not session.get('admin_authenticated'):
#         return redirect(url_for('login'))


@app.route('/')
def index():
    """Admin home page - Dashboard"""
    stats = get_evaluation_statistics()
    return render_template('dashboard.html', stats=stats)


@app.route('/evaluations')
def evaluations_list():
    """List all evaluations with search"""
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Load all evaluations
    evaluations = load_context_evaluations()
    
    # Apply search filter
    filtered = filter_evaluations(
        evaluations, 
        search_query=search_query
    )
    
    # Pagination
    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]
    
    # Calculate pagination info
    total_pages = (total + per_page - 1) // per_page
    
    return render_template(
        'evaluations_list.html',
        evaluations=paginated,
        search_query=search_query,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages
    )


@app.route('/evaluations/viewer')
def evaluation_viewer():
    """Interactive evaluation viewer with navigation"""
    eval_id = request.args.get('id')
    search_query = request.args.get('search', '').strip()
    
    # Load all evaluations
    evaluations = load_context_evaluations()
    
    # Apply filters to get the working set
    filtered = filter_evaluations(
        evaluations,
        search_query=search_query
    )
    
    if not filtered:
        return render_template('evaluation_viewer.html', 
                             evaluation=None, 
                             error="No evaluations found")
    
    # Find current evaluation
    current_idx = 0
    current_eval = None
    
    if eval_id:
        for idx, evaluation in enumerate(filtered):
            eval_key = evaluation.get('evaluation_id') or evaluation.get('id')
            if eval_key == eval_id:
                current_idx = idx
                current_eval = evaluation
                break
    
    # If not found or no ID provided, show first
    if current_eval is None:
        current_eval = filtered[0]
        current_idx = 0
    
    # Get prev/next evaluation IDs
    prev_id = filtered[current_idx - 1].get('evaluation_id') or filtered[current_idx - 1].get('id') if current_idx > 0 else None
    next_id = filtered[current_idx + 1].get('evaluation_id') or filtered[current_idx + 1].get('id') if current_idx < len(filtered) - 1 else None
    
    return render_template(
        'evaluation_viewer.html',
        evaluation=current_eval,
        current_index=current_idx + 1,
        total_count=len(filtered),
        prev_id=prev_id,
        next_id=next_id,
        search_query=search_query
    )


@app.route('/evaluations/<eval_id>')
def evaluation_detail(eval_id: str):
    """View single evaluation details"""
    evaluations = load_context_evaluations()
    
    evaluation = next(
        (e for e in evaluations if e.get('evaluation_id') == eval_id),
        None
    )
    
    if not evaluation:
        return render_template('evaluation_viewer.html', 
                             evaluation=None,
                             error=f"Evaluation {eval_id} not found")
    
    return render_template('evaluation_detail.html', evaluation=evaluation)


@app.route('/evaluations/<eval_id>/delete', methods=['POST'])
def delete_evaluation(eval_id):
    """Delete an evaluation"""
    from blob_storage_helper import delete_context_evaluation
    
    success = delete_context_evaluation(eval_id)
    
    if success:
        return jsonify({'success': True, 'message': f'Evaluation {eval_id} deleted successfully'})
    else:
        return jsonify({'success': False, 'message': f'Failed to delete evaluation {eval_id}'}), 404


@app.route('/api/evaluations/search')
def api_search_evaluations():
    """API endpoint for searching evaluations"""
    query = request.args.get('q', '').strip()
    status = request.args.get('status', 'all')
    
    evaluations = load_context_evaluations()
    filtered = filter_evaluations(evaluations, search_query=query, status_filter=status)
    
    # Return simplified list for API
    results = [
        {
            'evaluation_id': e.get('evaluation_id'),
            'timestamp': e.get('timestamp'),
            'user_approved': e.get('user_approved'),
            'category': e.get('detected_category'),
            'uat_numbers': e.get('suggested_uats', [])[:3],  # First 3
            'title': e.get('user_input', {}).get('issue_title', '')[:100]
        }
        for e in filtered
    ]
    
    return jsonify({'results': results, 'count': len(results)})


@app.route('/api/evaluations/export')
def api_export_evaluations():
    """Export evaluations as JSON"""
    search_query = request.args.get('search', '').strip()
    status = request.args.get('status', 'all')
    
    evaluations = load_context_evaluations()
    filtered = filter_evaluations(evaluations, search_query=query, status_filter=status)
    
    return jsonify({
        'export_date': datetime.now().isoformat(),
        'count': len(filtered),
        'evaluations': filtered
    })


def filter_evaluations(
    evaluations: List[Dict[str, Any]], 
    search_query: str = ''
) -> List[Dict[str, Any]]:
    """Filter evaluations based on search query"""
    filtered = evaluations
    
    # Filter by search query
    if search_query:
        query_lower = search_query.lower()
        filtered = [
            e for e in filtered
            if matches_search_query(e, query_lower)
        ]
    
    # Sort by timestamp (newest first)
    filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return filtered


def matches_search_query(evaluation: Dict[str, Any], query: str) -> bool:
    """Check if evaluation matches search query"""
    # Search in UAT numbers
    suggested_uats = evaluation.get('suggested_uats', [])
    for uat in suggested_uats:
        if query in uat.lower():
            return True
    
    # Search in user input
    user_input = evaluation.get('user_input', {})
    if query in user_input.get('issue_title', '').lower():
        return True
    if query in user_input.get('issue_description', '').lower():
        return True
    if query in user_input.get('expected_behavior', '').lower():
        return True
    
    # Search in category
    if query in evaluation.get('detected_category', '').lower():
        return True
    
    # Search in feature
    if query in evaluation.get('detected_feature', '').lower():
        return True
    
    # Search in evaluation ID
    if query in evaluation.get('evaluation_id', '').lower():
        return True
    
    return False


def get_evaluation_statistics() -> Dict[str, Any]:
    """Calculate statistics from evaluations"""
    evaluations = load_context_evaluations()
    
    total = len(evaluations)
    
    # Category breakdown
    category_counts = {}
    for e in evaluations:
        cat = e.get('detected_category', 'Unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Recent activity (last 7 days)
    from datetime import timedelta
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent = [e for e in evaluations if e.get('timestamp', '') > seven_days_ago]
    
    return {
        'total': total,
        'category_breakdown': category_counts,
        'recent_count': len(recent),
        'recent_evaluations': sorted(recent, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
    }


@app.route('/corrections')
def corrections_list():
    """View all corrections"""
    corrections_data = load_corrections()
    corrections = corrections_data.get('corrections', [])
    
    # Calculate stats
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_count = sum(1 for c in corrections if c.get('timestamp', '') > seven_days_ago)
    
    categories = set()
    for c in corrections:
        if c.get('correct_category'):
            categories.add(c.get('correct_category'))
    
    return render_template(
        'corrections_list.html',
        corrections=corrections,
        recent_count=recent_count,
        categories_count=len(categories)
    )


@app.route('/corrections/<int:index>/delete', methods=['POST'])
def delete_correction(index):
    """Delete a correction"""
    try:
        corrections_data = load_corrections()
        corrections = corrections_data.get('corrections', [])
        
        if 0 <= index < len(corrections):
            deleted = corrections.pop(index)
            corrections_data['corrections'] = corrections
            
            success = save_corrections(corrections_data)
            if success:
                return jsonify({'success': True, 'message': f'Correction deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'Failed to save changes'}), 500
        else:
            return jsonify({'success': False, 'message': 'Invalid index'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/health-dashboard')
def health_dashboard():
    """Service health monitoring dashboard"""
    return render_template('health.html')


@app.route('/logs')
def logs_viewer():
    """View application logs from Azure Log Analytics"""
    config = kv_config.get_config()
    logs_enabled = bool(config.get('AZURE_LOG_ANALYTICS_WORKSPACE_ID'))
    return render_template('logs.html', logs_enabled=logs_enabled)


if __name__ == '__main__':
    print("=" * 80)
    print("🔧 Admin Service Starting")
    print("=" * 80)
    print(f"Port: 8004")
    config = kv_config.get_config()
    print(f"Environment: {config.get('AZURE_OPENAI_ENDPOINT', 'Not configured')}")
    print(f"Storage: Azure Blob Storage (stgcsdevgg4a6y)")
    print("=" * 80)
    print("\nAdmin Routes:")
    print("  http://localhost:8004/                    - Admin Dashboard")
    print("  http://localhost:8004/evaluations         - Evaluations List")
    print("  http://localhost:8004/evaluations/viewer  - Interactive Viewer")
    print("  http://localhost:8004/corrections         - Corrections Database")
    print("  http://localhost:8004/health-dashboard    - Service Health Monitor")
    print("  http://localhost:8004/logs                - Application Logs Viewer")
    print("=" * 80)
    
    if TELEMETRY_ENABLED:
        print("\n✅ Telemetry & Monitoring:")
        print("  • Application Insights - Request tracking enabled")
        print("  • Azure Log Analytics - Log viewing available")
    else:
        print("\n⚠️  Telemetry disabled - install opencensus-ext-azure for full monitoring")
    
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=8008, debug=True)
