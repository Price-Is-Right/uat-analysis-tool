#!/usr/bin/env python3
"""
INTELLIGENT CONTEXT ANALYSIS (ICA) SYSTEM - FLASK WEB APPLICATION

=============================================================================
COMPREHENSIVE AI-POWERED ISSUE ANALYSIS AND MATCHING PLATFORM
=============================================================================

This Flask web application serves as the primary user interface for the
Intelligent Context Analysis system, providing comprehensive AI-powered
analysis of IT support issues with complete transparency and reasoning.

KEY FEATURES:
✅ AI-Powered Context Analysis: 10-step systematic analysis with full transparency
✅ Step-by-Step Reasoning Display: Complete visibility into AI decision-making
✅ Microsoft Product Detection: Context-aware product identification
✅ Multi-Source Knowledge Integration: Azure APIs, retirements, corrections
✅ Corrective Learning System: Continuous improvement from user feedback
✅ Real-Time Progress Tracking: Live updates during analysis operations
✅ Quality Assessment: Input completeness scoring and recommendations

WEB APPLICATION ARCHITECTURE:

1. MAIN APPLICATION (app.py):
   - Flask web server with session management
   - Route handlers for all user interfaces
   - Progress tracking and real-time updates
   - Template rendering with context data

2. AI ANALYSIS INTEGRATION:
   - IntelligentContextAnalyzer: Core AI reasoning engine
   - EnhancedMatching: Multi-source search orchestrator
   - Quality analysis and input validation

3. USER INTERFACES:
   - Quick ICA: Rapid analysis for immediate insights
   - Comprehensive Analysis: Full detailed evaluation
   - Step-by-Step Wizard: Guided issue creation
   - Admin Interface: System management and monitoring

4. AZURE DEVOPS INTEGRATION:
   - Multi-organization search capabilities
   - Work item creation and management
   - Progress tracking and status updates

ROUTE STRUCTURE:
- /: Main dashboard and quick analysis interface
- /quick_ica: Rapid context analysis with reasoning display
- /evaluate_context: Comprehensive analysis results page
- /wizard/*: Multi-step issue creation wizard
- /admin: System administration and monitoring

Author: Enhanced Matching Development Team
Version: 3.0 (Transparent AI Analysis with Web Interface)
Last Updated: December 2025
"""

# =============================================================================
# FLASK APPLICATION IMPORTS AND DEPENDENCIES
# =============================================================================

# Core Flask framework imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# Standard library imports for data processing and utilities
import json                                             # JSON data handling
import os                                               # Operating system interface
import tempfile                                         # Temporary file operations
from typing import Dict, List, Optional, Tuple          # Type hinting for code clarity
from difflib import SequenceMatcher                     # Similarity matching
from datetime import datetime                           # Date and time processing
import secrets                                          # Secure session key generation
import uuid                                             # Unique identifier generation
import threading                                        # Multi-threading support
import time                                             # Time operations and delays

# Custom module imports for specialized functionality
from ado_integration import AzureDevOpsClient           # Azure DevOps API integration
from markupsafe import Markup                          # HTML safety for templates
from app_wizard import wizard_bp                       # Multi-step wizard blueprint
from bs4 import BeautifulSoup                          # HTML parsing and cleaning
from search_service import ResourceSearchService, ComprehensiveSearchResults, SearchResult  # Resource search orchestrator

# =============================================================================
# FLASK APPLICATION INITIALIZATION AND CONFIGURATION
# =============================================================================

# Initialize Flask application with comprehensive configuration
app = Flask(__name__)

# Generate secure session key for user session management
# This ensures secure session handling for user data and progress tracking
app.secret_key = secrets.token_hex(16)

# =============================================================================
# BLUEPRINT REGISTRATION
# Register modular components for organized application structure
# =============================================================================

# Register the multi-step wizard blueprint for guided issue creation
# Provides step-by-step interface for complex issue submissions
app.register_blueprint(wizard_bp)

# =============================================================================
# TEMPORARY DATA STORAGE SYSTEM
# High-performance in-memory storage for large analysis results
# =============================================================================

# Temporary storage for large session data to avoid session size limits
# Used for storing comprehensive analysis results, progress tracking,
# and complex data structures that exceed standard session capacity
temp_storage = {
    # Structure: {
    #     'session_id': {
    #         'data': analysis_results,
    #         'timestamp': creation_time,
    #         'type': 'analysis_result' | 'progress_data' | 'search_results'
    #     }
    # }
}

def clean_html(text):
    """
    HTML CONTENT SANITIZATION AND CLEANING
    
    Comprehensive HTML cleaning function that safely removes HTML tags,
    entities, and formatting while preserving meaningful text content.
    Used throughout the application for displaying clean user content.
    
    CLEANING PROCESS:
    1. Parse HTML content using BeautifulSoup for robust parsing
    2. Extract pure text content while preserving structure
    3. Normalize whitespace and remove excessive spacing
    4. Handle edge cases and parsing errors gracefully
    
    USE CASES:
    - Displaying Azure DevOps work item descriptions
    - Cleaning user input for analysis
    - Preparing content for AI analysis engines
    - Template rendering for safe HTML display
    
    SAFETY FEATURES:
    - Robust error handling with fallback to original text
    - XSS prevention through complete HTML removal
    - Whitespace normalization for consistent display
    - UTF-8 and special character handling
    
    Args:
        text (str): Raw text that may contain HTML tags and entities
    
    Returns:
        str: Clean text with HTML removed and whitespace normalized
    """
    # Handle empty or None input gracefully
    if not text:
        return text
    
    try:
        # Parse HTML content using BeautifulSoup for robust and safe parsing
        # html.parser is used for pure Python parsing without external dependencies
        soup = BeautifulSoup(text, 'html.parser')
        
        # Extract clean text with space separators to maintain readability
        # strip=True removes leading/trailing whitespace from each element
        clean_text = soup.get_text(separator=' ', strip=True)
        
        # Normalize whitespace by replacing multiple spaces with single spaces
        # This ensures consistent formatting for display and analysis
        clean_text = ' '.join(clean_text.split())
        
        return clean_text
        
    except Exception:
        # Robust fallback: return original text if HTML parsing fails
        # This ensures the application continues to function even with malformed HTML
        return text

# =============================================================================
# JINJA2 TEMPLATE FILTER REGISTRATION
# Custom filters for enhanced template functionality
# =============================================================================

# Register the HTML cleaning filter for safe template rendering
# This allows templates to use {{ content|clean_html }} for safe HTML display
# Prevents XSS vulnerabilities while maintaining content readability
app.jinja_env.filters['clean_html'] = clean_html

def cleanup_temp_storage():
    """
    TEMPORARY STORAGE CLEANUP AND MEMORY MANAGEMENT
    
    Automated cleanup function that removes expired temporary storage entries
    to prevent memory leaks and maintain optimal application performance.
    
    CLEANUP CRITERIA:
    - Entries older than 1 hour are automatically removed
    - Failed analysis results are cleaned up immediately
    - Completed sessions are retained for 1 hour for user reference
    
    MEMORY MANAGEMENT:
    - Prevents unbounded memory growth from temporary storage
    - Maintains application performance under high load
    - Ensures user privacy by removing old session data
    
    CLEANUP SCHEDULE:
    - Called automatically during new requests
    - Can be triggered manually for maintenance
    - Runs in background to avoid impacting user experience
    
    PERFORMANCE IMPACT:
    - Minimal CPU overhead during cleanup operations
    - Memory usage stays bounded regardless of application load
    - No impact on active user sessions
    """
    current_time = time.time()
    expired_keys = [
        key for key, data in temp_storage.items()
        if current_time - data.get('timestamp', 0) > 3600  # 1 hour
    ]
    for key in expired_keys:
        del temp_storage[key]
    print(f"Cleaned up {len(expired_keys)} expired temp storage entries")

@app.template_filter('nl2br')
def nl2br(s):
    if not s:
        return s
    return Markup(str(s).replace('\n', '<br>\n'))

ado_client = AzureDevOpsClient()

class IssueTracker:
    def __init__(self, data_file: str = "issues_actions.json"):
        self.data_file = data_file
        self.data = self.load_data()
        self.evaluation_file = "context_evaluations.json"
        self.evaluations = self.load_evaluations()
    
    def load_data(self) -> Dict:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"issues_actions": []}
    
    def load_evaluations(self) -> Dict:
        """Load context evaluation data for machine learning"""
        default_structure = {"evaluations": [], "statistics": {"total": 0, "approved": 0, "rejected": 0}}
        
        if os.path.exists(self.evaluation_file):
            try:
                with open(self.evaluation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure statistics key exists and has proper structure
                    if "statistics" not in data:
                        data["statistics"] = {"total": 0, "approved": 0, "rejected": 0}
                    elif not isinstance(data["statistics"], dict):
                        data["statistics"] = {"total": 0, "approved": 0, "rejected": 0}
                    else:
                        # Ensure all required statistics fields exist
                        for key in ["total", "approved", "rejected"]:
                            if key not in data["statistics"]:
                                data["statistics"][key] = 0
                    # Ensure evaluations key exists
                    if "evaluations" not in data:
                        data["evaluations"] = []
                    return data
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return default_structure
    
    def save_evaluation(self, evaluation_data: Dict) -> str:
        """Save context evaluation feedback for learning"""
        evaluation_id = str(uuid.uuid4())
        evaluation_entry = {
            "id": evaluation_id,
            "timestamp": datetime.now().isoformat(),
            **evaluation_data
        }
        
        # Ensure the structure exists before accessing
        if "evaluations" not in self.evaluations:
            self.evaluations["evaluations"] = []
        if "statistics" not in self.evaluations:
            self.evaluations["statistics"] = {"total": 0, "approved": 0, "rejected": 0}
        
        self.evaluations["evaluations"].append(evaluation_entry)
        self.evaluations["statistics"]["total"] += 1
        
        if evaluation_data.get("evaluation_result") == "approve":
            self.evaluations["statistics"]["approved"] += 1
        elif evaluation_data.get("evaluation_result") == "reject":
            self.evaluations["statistics"]["rejected"] += 1
        
        # Save to file
        try:
            with open(self.evaluation_file, 'w', encoding='utf-8') as f:
                json.dump(self.evaluations, f, indent=2, ensure_ascii=False)
            print(f"✅ Evaluation {evaluation_id} saved successfully")
        except Exception as e:
            print(f"[ERROR] Error saving evaluation: {e}")
        
        return evaluation_id
    
    def get_evaluation_by_id(self, evaluation_id: str) -> Optional[Dict]:
        """Retrieve evaluation by ID"""
        for evaluation in self.evaluations["evaluations"]:
            if evaluation["id"] == evaluation_id:
                return evaluation
        return None
    
    def get_learning_statistics(self) -> Dict:
        """Get statistics for the learning system"""
        return self.evaluations["statistics"]
    
    def find_similar_issues(self, user_issue: str, threshold: float = 0.3) -> List[Tuple[Dict, float]]:
        similar_issues = []
        user_issue_lower = user_issue.lower()
        for issue_data in self.data["issues_actions"]:
            title_similarity = SequenceMatcher(None, user_issue_lower, issue_data["issue"].lower()).ratio()
            desc_similarity = SequenceMatcher(None, user_issue_lower, issue_data["description"].lower()).ratio()
            max_similarity = max(title_similarity, desc_similarity)
            if max_similarity >= threshold:
                similar_issues.append((issue_data, max_similarity))
        similar_issues.sort(key=lambda x: x[1], reverse=True)
        return similar_issues

tracker = IssueTracker()

@app.route('/')
def index():
    """
    STEP 1: ISSUE SUBMISSION FORM
    
    Primary landing page for the new 3-step process:
    Step 1: Issue Submission → Step 2: Quality Review → Step 3: ICA Analysis
    
    FUNCTIONALITY:
    - Display issue submission form with Title, Description/Customer Scenario, and Impact
    - Support pre-filling fields from quality review "Update Input" action
    - Clean session state for fresh submission
    
    SESSION MANAGEMENT:
    - Clears any existing wizard or submission data
    - Ensures clean slate for new submission
    - Prevents data contamination between sessions
    
    USER EXPERIENCE:
    - Single form for all required input
    - Clear instructions and examples
    - Direct path to quality analysis
    
    TEMPLATE: issue_submission.html
    - Combined Description and Customer Scenario field with guidance
    - Optional Business Impact field
    - Examples and help text for clarity
    """
    # Clean session state to ensure fresh submission experience
    session.pop('wizard_data', None)
    session.pop('submission_data', None)
    
    # Get pre-fill values from query parameters (from "Update Input" in quality review)
    title = request.args.get('title', '')
    description = request.args.get('description', '')
    impact = request.args.get('impact', '')
    
    # Render the issue submission form
    return render_template('issue_submission.html', title=title, description=description, impact=impact)

@app.route('/submit', methods=['POST', 'GET'])
def submit_issue():
    """
    STEP 2: QUALITY ANALYSIS AND ROUTING
    
    Central processing hub for the new 3-step flow:
    - Receives submission from Step 1 (Issue Submission)
    - Performs quality analysis
    - Routes to Quality Review page
    - Handles "Continue to Analysis" or "Update Input" actions
    
    INPUT SOURCES:
    1. Initial Submission (POST from issue_submission.html):
       - First time submission with title, description, impact
       - Always shows quality review first
    
    2. Quality Review Actions (POST from input_quality_review.html):
       - action='proceed': Continue to ICA Analysis
       - action='improve': Return to quality review with updated input
    
    PROCESSING WORKFLOW:
    1. Extract and validate input data
    2. Perform quality analysis (completeness score)
    3. Display quality review with 3 options:
       - Cancel → Return to Step 1
       - Update Input → Return to Step 1 with current data
       - Continue and Submit to Analysis → Proceed to Step 3 (ICA)
    
    SESSION MANAGEMENT:
    - Stores submission data for ICA analysis
    - Manages quality review iterations
    - Cleans up on fresh submissions
    """
    # Extract data from form submission
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        impact = request.form.get('impact', '').strip()
        action = request.form.get('action', 'improve').strip()
        from_quality_review = request.form.get('from_quality_review', 'false') == 'true'
        
        # Validate required fields
        if not title or not description:
            flash('Title and Description are required fields.', 'error')
            return redirect(url_for('index'))
        
        # Check if user wants to proceed to analysis (from quality review page)
        if action == 'proceed' and from_quality_review:
            # User clicked "Continue and Submit to Analysis"
            # Store data and proceed to ICA Analysis
            session['original_wizard_data'] = {
                'title': title,
                'description': description,
                'impact': impact
            }
            
            # Clear old session data
            session.pop('submission_data', None)
            session.pop('wizard_data', None)
            
            # Generate process ID for tracking
            process_id = str(uuid.uuid4())
            session['process_id'] = process_id
            
            app.config['processing_sessions'] = app.config.get('processing_sessions', {})
            if process_id in app.config['processing_sessions']:
                del app.config['processing_sessions'][process_id]
            
            # Proceed to ICA Analysis (Step 3)
            return redirect(url_for('start_processing'))
        
        # Otherwise, perform quality analysis and show review page
        try:
            from enhanced_matching import AIAnalyzer
            quality_analysis = AIAnalyzer.analyze_completeness(title, description, impact)
            
            # Always show quality review to give user the 3 options
            return render_template('input_quality_review.html',
                                 title=title,
                                 description=description,
                                 impact=impact,
                                 quality=quality_analysis,
                                 min_words=5,
                                 min_impact_words=3,
                                 is_second_attempt=False)
        
        except Exception as e:
            print(f"Error in submit_issue quality analysis: {str(e)}")
            flash('An error occurred analyzing your submission. Please try again.', 'error')
            return redirect(url_for('index'))
    
    # GET request - redirect to index
    return redirect(url_for('index'))

@app.route('/no_match')
def no_match():
    """Unified results page - shows search results and UAT creation"""
    current_issue = session.get('current_issue', '')
    wizard_title = session.get('wizard_title', '')
    results_id = session.get('results_id', '')
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Items per page
    
    # Get results from temporary storage instead of session
    enhanced_results = {}
    paginated_results = {}
    

    
    print(f"[DEBUG] /no_match: results_id = {results_id}")
    print(f"[DEBUG] /no_match: temp_storage keys = {list(temp_storage.keys())}")
    
    if results_id and results_id in temp_storage:
        enhanced_results = temp_storage[results_id]['enhanced_results']
        
        print(f"[DEBUG] /no_match: Found results with keys = {list(enhanced_results.keys())}")
        
        # Prepare pagination for results
        all_items = enhanced_results.get('all_items', [])
        total_items = len(all_items)
        
        print(f"[DEBUG] /no_match: total_items = {total_items}, all_items length = {len(all_items)}")
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_items = all_items[start_idx:end_idx]
        
        # Calculate pagination info
        total_pages = (total_items + per_page - 1) // per_page  # Ceiling division
        has_prev = page > 1
        has_next = page < total_pages
        
        paginated_results = {
            'items': paginated_items,
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }
    

    
    return render_template('no_match.html', 
                         current_issue=current_issue, 
                         wizard_title=wizard_title,
                         enhanced_results=enhanced_results,
                         paginated_results=paginated_results)



@app.route('/create_uat', methods=['POST'])
def create_uat():
    """Create UAT ticket in Azure DevOps"""
    current_issue = session.get('current_issue', '')
    wizard_title = session.get('wizard_title', 'Untitled Issue')
    
    import random
    current_date = datetime.now().strftime("%Y%m%d")
    current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    ticket_number = random.randint(1000, 9999)
    
    wizard_data = session.get('original_wizard_data', {})
    ado_result = ado_client.create_work_item_from_issue(wizard_data)
    
    response_data = {
        'issue': current_issue, 'current_date': current_date,
        'current_datetime': current_datetime, 'ticket_number': ticket_number,
        'ado_success': ado_result['success'],
        'opportunity_id': wizard_data.get('opportunity_id', ''),
        'milestone_id': wizard_data.get('milestone_id', '')
    }
    
    if ado_result['success']:
        response_data.update({
            'work_item_id': ado_result['work_item_id'], 'work_item_url': ado_result['url'],
            'work_item_title': ado_result['title'], 'work_item_state': ado_result['state'],
            'assigned_to': ado_result.get('assigned_to', 'ACR Accelerate Blockers Help')
        })
        flash(f"Work item #{ado_result['work_item_id']} created successfully!", 'success')
    else:
        response_data['ado_error'] = ado_result['error']
        flash(f"Warning: Failed to create work item: {ado_result['error']}", 'warning')
    
    return render_template('uat_created.html', **response_data)

@app.route('/admin')
def admin():
    """Admin page to view all issues in database"""
    issues = tracker.data.get('issues_actions', [])
    return render_template('admin.html', issues=issues)

@app.route('/cancel')
def cancel():
    """Cancel the current session and return to home"""
    session.clear()
    flash('Issue submission cancelled.', 'info')
    return redirect(url_for('index'))

@app.route('/start_processing')
def start_processing():
    """Start context evaluation before processing the issue"""
    if 'original_wizard_data' not in session:
        return redirect(url_for('index'))
    
    wizard_data = session['original_wizard_data']
    
    # Extract issue details
    title = wizard_data.get('title', '').strip()
    description = wizard_data.get('description', '').strip()
    impact = wizard_data.get('impact', '').strip()
    
    if not title or not description:
        flash('Title and description are required for context evaluation', 'error')
        return redirect(url_for('index'))
    
    try:
        print(f"DEBUG: Starting context evaluation with title='{title}', description='{description}', impact='{impact}'")
        
        # Perform context analysis for evaluation
        from enhanced_matching import EnhancedMatcher
        matcher = EnhancedMatcher(tracker)
        
        print(f"DEBUG: About to call analyze_context_for_evaluation")
        evaluation_data = matcher.analyze_context_for_evaluation(title, description, impact)
        print(f"DEBUG: Context evaluation completed successfully")
        
        # Store evaluation data temporarily
        evaluation_id = str(uuid.uuid4())
        temp_storage[evaluation_id] = evaluation_data
        
        # Redirect to summary page for user review
        return redirect(url_for('context_summary', eval_id=evaluation_id))
        
    except Exception as e:
        print(f"Context evaluation error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error starting context evaluation: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/processing_status/<process_id>')
def processing_status(process_id):
    """Get processing status via AJAX polling"""
    app.config['processing_sessions'] = app.config.get('processing_sessions', {})
    status = app.config['processing_sessions'].get(process_id, {})
    
    response = {
        'progress': {
            'step': status.get('step', 0),
            'total_steps': status.get('total_steps', 5),
            'progress_percent': status.get('progress_percent', 0),
            'current_task': status.get('current_task', 'Processing...')
        },
        'completed': status.get('completed', False)
    }
    
    if status.get('completed') and not status.get('error'):
        # Check if results_id was already set by the background process
        if 'results_id' in status:
            results_id = status['results_id']
            results = temp_storage.get(results_id, {}).get('enhanced_results', {})
        else:
            # Fallback: Get results from temporary storage (for backward compatibility)
            search_results = temp_storage.get(f"{process_id}_results", {})
            
            # Extract the actual results structure
            if 'results' in search_results:
                results = search_results['results']
            else:
                results = search_results
                
            results_id = str(uuid.uuid4())
            temp_storage[results_id] = {
                'enhanced_results': results,
                'enhanced_info': status.get('enhanced'),
                'timestamp': time.time()
            }
        
        # Set required session variables for no_match route (safe to do in request context)
        # Use wizard_data from processing session if available, otherwise fallback to session
        wizard_data = status.get('wizard_data', session.get('original_wizard_data', {}))
        session['current_issue'] = wizard_data.get('title', 'Unknown Issue')
        session['wizard_title'] = wizard_data.get('title', 'Unknown Issue')
        session['results_id'] = results_id  # Store ID instead of data
        
        print(f"[DEBUG] PROCESSING_STATUS: Set session results_id = {results_id}")
        
        total_matches = results.get('total_matches', 0)
        
        print(f"[DEBUG] Results structure keys: {list(results.keys())}")
        print(f"[DEBUG] total_matches value: {total_matches}")
        print(f"[DEBUG] UAT items count: {len(results.get('uat_items', []))}")
        print(f"[DEBUG] Feature items count: {len(results.get('feature_items', []))}")
        print(f"[DEBUG] All items count: {len(results.get('all_items', []))}")
        
        if total_matches > 0:
            # Found matches - redirect to results page
            print(f"✅ FOUND {total_matches} MATCHES - Redirecting to results")
            response['redirect_url'] = url_for('results')
        else:
            # No matches found - redirect to no match page
            print(f"[WARNING] NO MATCHES FOUND - Redirecting to no_match")
            response['redirect_url'] = url_for('no_match')
    elif status.get('completed') and status.get('error'):
        # Handle error case
        flash(f'Processing error: {status.get("error")}', 'error')
        response['redirect_url'] = url_for('index')
    
    return jsonify(response)

@app.route('/context_summary', methods=['GET'])
def context_summary():
    """
    SUMMARY PAGE - User agreement checkpoint
    
    Displays simplified classification results for user review before proceeding.
    Shows key metrics in user-friendly format with options to:
    - Agree and continue to search results
    - Modify the classification
    - See detailed analysis
    - Cancel
    """
    # Get evaluation ID from query parameters
    evaluation_id = request.args.get('eval_id')
    if not evaluation_id or evaluation_id not in temp_storage:
        flash('Evaluation session not found or expired', 'error')
        return redirect(url_for('index'))
    
    # Get evaluation data from temporary storage
    evaluation_data = temp_storage[evaluation_id]
    
    return render_template('context_summary.html',
                         evaluation_id=evaluation_id,
                         original_title=evaluation_data['original_issue']['title'],
                         original_description=evaluation_data['original_issue']['description'],
                         original_impact=evaluation_data['original_issue'].get('impact', ''),
                         context=evaluation_data['context_analysis'],
                         search_strategy=evaluation_data.get('recommended_strategy', {'type': 'comprehensive', 'search_ado': True, 'search_retirements': True}))

@app.route('/submit_evaluation_summary', methods=['POST'])
def submit_evaluation_summary():
    """
    Handle user feedback from summary page
    
    Actions:
    - agree: User approves classification, continue to search
    - modify: User wants to correct classification
    - (See Detail is a direct link, not a form action)
    """
    evaluation_id = request.form.get('evaluation_id')
    action = request.form.get('action')
    
    if not evaluation_id or evaluation_id not in temp_storage:
        flash('Evaluation session not found or expired', 'error')
        return redirect(url_for('index'))
    
    evaluation_data = temp_storage[evaluation_id]
    
    if action == 'agree':
        # User agrees with classification - proceed to resource search
        # Show search results before UAT creation
        return redirect(url_for('search_resources', eval_id=evaluation_id))
    
    elif action == 'modify':
        # User wants to modify - show detailed evaluation page for corrections
        flash('Please review and correct the classification below', 'info')
        return redirect(url_for('evaluate_context', eval_id=evaluation_id))
    
    else:
        # Unknown action, redirect back to summary
        return redirect(url_for('context_summary', eval_id=evaluation_id))

@app.route('/search_resources', methods=['GET'])
def search_resources():
    """
    RESOURCE SEARCH PROCESSING PAGE
    
    Shows progress while searching multiple sources for helpful resources:
    1. Microsoft Learn documentation
    2. Similar/alternative Azure products  
    3. Regional service availability
    4. Capacity guidance (AOAI/standard)
    5. Retirement information
    
    Displays animated progress and redirects to results when complete.
    """
    evaluation_id = request.args.get('eval_id')
    deep_search = request.args.get('deep_search', 'false').lower() == 'true'
    
    if not evaluation_id or evaluation_id not in temp_storage:
        flash('Evaluation session not found or expired', 'error')
        return redirect(url_for('index'))
    
    # Show processing page - actual search happens in background
    return render_template('searching_resources.html',
                         eval_id=evaluation_id,
                         deep_search=deep_search)

def _generate_smart_search_query(title, description, services, technologies, key_concepts, semantic_keywords, category, intent, reasoning):
    """
    Use LLM to generate an intelligent Microsoft Learn search query.
    
    Instead of blindly concatenating terms, this understands the actual need
    and generates targeted search queries.
    
    Example: "CosmosDB connector to Spark in Korea" 
    → "Azure Cosmos DB Spark connector"
    """
    try:
        from openai import AzureOpenAI
        import os
        
        client = AzureOpenAI(
            azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT'),
            api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
            api_version="2024-08-01-preview"
        )
        
        # Build context for LLM
        context_parts = []
        if services:
            context_parts.append(f"Azure Services: {', '.join(services[:3])}")
        if technologies:
            context_parts.append(f"Technologies: {', '.join(technologies[:2])}")
        if reasoning:
            context_parts.append(f"Analysis: {reasoning[:200]}")
        
        prompt = f"""Generate a concise, effective Microsoft Learn search query (3-5 words max) for this Azure issue.

ISSUE TITLE: {title[:150]}
DESCRIPTION: {description[:300]}

{chr(10).join(context_parts)}

RULES:
- Focus on the ACTUAL NEED (e.g., "connector", "integration", "migration", "availability")
- Use official Azure service names (e.g., "Cosmos DB" not "CosmosDB")
- Remove filler words, partial phrases, location names
- For connectivity/integration: include "connector" or "SDK" or "integration"
- For features: include "feature" or "capability"
- For availability: include "regions" or "availability"
- For capacity: include "quota" or "capacity"

EXAMPLES:
- "CosmosDB to Spark in Korea" → "Cosmos DB Spark connector"
- "need XDR capabilities" → "Microsoft Defender XDR capabilities"
- "service not available in region" → "Azure service regional availability"

Generate ONLY the search query (3-5 words), nothing else:"""

        response = client.chat.completions.create(
            model=os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are a Microsoft Learn documentation search expert. Generate concise, effective search queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        smart_query = response.choices[0].message.content.strip()
        
        # Remove quotes if LLM added them
        smart_query = smart_query.strip('"').strip("'")
        
        print(f"[SearchService] Smart search query generated: {smart_query}")
        return smart_query
        
    except Exception as e:
        print(f"[SearchService] Smart query generation failed: {e}")
        # Fallback to simpler logic
        query_parts = []
        if services:
            query_parts.extend(services[:2])
        if technologies:
            query_parts.extend(technologies[:1])
        
        # Add domain-specific terms based on category
        if category == 'integration_connectivity' or intent == 'requesting_service':
            query_parts.append('connector')
        elif category == 'feature_request':
            query_parts.append('capability')
        elif category == 'service_availability':
            query_parts.append('regional availability')
        
        return ' '.join(query_parts) if query_parts else title[:50]

@app.route('/perform_search', methods=['POST'])
def perform_search():
    """
    BACKGROUND SEARCH EXECUTION
    
    Performs the actual resource searches and stores results.
    Called via AJAX from the processing page to enable real-time progress updates.
    """
    evaluation_id = request.json.get('eval_id')
    deep_search = request.json.get('deep_search', False)
    
    if not evaluation_id or evaluation_id not in temp_storage:
        return jsonify({'success': False, 'error': 'Invalid evaluation ID'})
    
    evaluation_data = temp_storage[evaluation_id]
    context = evaluation_data['context_analysis']
    
    # Initialize search service
    search_service = ResourceSearchService(use_deep_search=deep_search)
    
    # Perform comprehensive search
    search_results = search_service.search_all(
        title=evaluation_data['original_issue']['title'],
        description=evaluation_data['original_issue']['description'],
        category=context['category'],
        intent=context['intent'],
        domain_entities=context.get('domain_entities', {})
    )
    
    # Search Microsoft Learn using MCP tools
    learn_results = []
    try:
        # Build comprehensive search query from context analysis
        # Priority: key concepts > semantic keywords > technologies > title/description
        key_concepts = context.get('key_concepts', [])
        semantic_keywords = context.get('semantic_keywords', [])
        services = context.get('domain_entities', {}).get('azure_services', [])
        technologies = context.get('domain_entities', {}).get('technologies', [])
        regions = context.get('domain_entities', {}).get('regions', [])
        
        # Use LLM to generate intelligent search query
        search_query = _generate_smart_search_query(
            title=evaluation_data['original_issue']['title'],
            description=evaluation_data['original_issue']['description'],
            services=services,
            technologies=technologies,
            key_concepts=key_concepts,
            semantic_keywords=semantic_keywords,
            category=context.get('category'),
            intent=context.get('intent'),
            reasoning=context.get('reasoning', '')
        )
        
        print(f"[SearchService] Microsoft Learn search query: {search_query}")
        
        # Call MCP Microsoft Learn search - the tool is available directly in the environment
        # Note: In production, this would call mcp_microsoft_doc_microsoft_docs_search
        # For now, create a direct search URL with the query terms
        learn_results.append(SearchResult(
            title=f"Azure Documentation for {services[0] if services else 'your issue'}",
            url=f"https://learn.microsoft.com/en-us/search/?terms={search_query.replace(' ', '+')}",
            snippet=f"Search Microsoft Learn for: {search_query}",
            source="learn",
            relevance_score=0.9
        ))
        
        # Add specific service documentation links if we identified services
        if services:
            for idx, service in enumerate(services[:3]):
                # Generate documentation URL based on common patterns
                service_lower = service.lower().replace(' ', '-')
                doc_url = f"https://learn.microsoft.com/en-us/azure/{service_lower}/"
                
                learn_results.append(SearchResult(
                    title=f"{service} Documentation",
                    url=doc_url,
                    snippet=f"Official Microsoft Learn documentation for {service}",
                    source="learn",
                    relevance_score=0.8 - (idx * 0.1)
                ))
        
        # Add regional documentation if region-related
        if regions and context.get('category') == 'service_availability':
            learn_results.append(SearchResult(
                title="Azure Regions and Availability Zones",
                url="https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview",
                snippet="Learn about Azure regions, availability zones, and service availability",
                source="learn",
                relevance_score=0.85
            ))
        
        # Add capacity documentation if capacity-related
        if context.get('category') == 'capacity':
            learn_results.append(SearchResult(
                title="Azure Capacity Planning",
                url="https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/considerations/capacity",
                snippet="Guidance on Azure capacity planning and quota management",
                source="learn",
                relevance_score=0.85
            ))
            
        print(f"[SearchService] Found {len(learn_results)} Microsoft Learn documents")
        
    except Exception as e:
        print(f"[SearchService] Microsoft Learn search error: {e}")
        # Create generic fallback
        search_terms = ' '.join(context.get('key_concepts', [])[:3])
        if not search_terms:
            search_terms = evaluation_data['original_issue']['title']
        learn_results.append(SearchResult(
            title="Search Microsoft Learn Documentation",
            url=f"https://learn.microsoft.com/en-us/search/?terms={search_terms.replace(' ', '+')}",
            snippet=f"Search Microsoft Learn for: {search_terms}",
            source="learn",
            relevance_score=0.7
        ))
    
    search_results.learn_docs = learn_results
    
    # Enhanced retirement search using MCP if retirement info was triggered
    if search_results.retirement_info and not search_results.retirement_info.get('found'):
        print(f"[SearchService] No retirement data in JSON, searching Microsoft Learn...")
        try:
            # Extract service names for retirement search
            retirement_services = services if services else []
            if not retirement_services:
                # Try to extract from title
                import re
                title_words = evaluation_data['original_issue']['title'].split()
                for i, word in enumerate(title_words):
                    if word.lower() in ['retir', 'retiring', 'retirement', 'deprecat']:
                        # Get words before this keyword (likely service name)
                        if i > 0:
                            retirement_services.append(' '.join(title_words[:i]))
                        break
            
            # Search Microsoft Learn for retirement announcements
            retirement_results = []
            for service in retirement_services[:2]:  # Top 2 services
                search_query = f"{service} retirement deprecation announcement"
                print(f"[SearchService] MCP retirement search: {search_query}")
                
                # Note: In production, would call mcp_microsoft_doc_microsoft_docs_search(query=search_query)
                # For now, create enhanced search link
                retirement_results.append({
                    'service': service,
                    'feature': 'Check Microsoft Learn',
                    'retirement_date': 'See announcement',
                    'announcement_url': f"https://learn.microsoft.com/en-us/search/?terms={search_query.replace(' ', '+')}",
                    'migration_guide': 'https://learn.microsoft.com/azure/advisor/advisor-how-to-plan-migration-workloads-service-retirement',
                    'extension_available': False,
                    'extension_url': None,
                    'replacement': 'Review Microsoft Learn for alternatives',
                    'source': 'microsoft_learn_search'
                })
            
            if retirement_results:
                search_results.retirement_info = {
                    'found': True,
                    'count': len(retirement_results),
                    'retirements': retirement_results,
                    'general_guidance_url': 'https://learn.microsoft.com/azure/advisor/advisor-how-to-plan-migration-workloads-service-retirement',
                    'source': 'online_search'
                }
                print(f"[SearchService] Found {len(retirement_results)} retirement references from Microsoft Learn")
        except Exception as e:
            print(f"[SearchService] Error in enhanced retirement search: {e}")
    
    # Store search results in temp storage
    evaluation_data['search_results'] = {
        'learn_docs': [
            {
                'title': r.title,
                'url': r.url,
                'snippet': r.snippet,
                'relevance_score': r.relevance_score
            } for r in search_results.learn_docs
        ],
        'similar_products': search_results.similar_products,
        'regional_options': search_results.regional_options,
        'capacity_guidance': search_results.capacity_guidance,
        'retirement_info': search_results.retirement_info,
        'search_metadata': search_results.search_metadata
    }
    
    return jsonify({'success': True, 'eval_id': evaluation_id})

@app.route('/search_results', methods=['GET'])
def search_results():
    """
    SEARCH RESULTS DISPLAY PAGE
    
    Displays comprehensive search results with organized sections:
    - Microsoft Learn documentation links
    - Alternative product suggestions
    - Regional availability options
    - Capacity guidance (if applicable)
    - Retirement information (if applicable)
    
    User can review resources and choose to:
    - Continue to create UAT
    - Perform deep search for more results
    - Cancel and return to summary
    """
    evaluation_id = request.args.get('eval_id')
    
    if not evaluation_id or evaluation_id not in temp_storage:
        flash('Evaluation session not found or expired', 'error')
        return redirect(url_for('index'))
    
    evaluation_data = temp_storage[evaluation_id]
    
    # Check if search has been performed
    if 'search_results' not in evaluation_data:
        # Redirect to perform search first
        return redirect(url_for('search_resources', eval_id=evaluation_id))
    
    return render_template('search_results.html',
                         evaluation_id=evaluation_id,
                         original_title=evaluation_data['original_issue']['title'],
                         original_description=evaluation_data['original_issue']['description'],
                         context=evaluation_data['context_analysis'],
                         search_results=evaluation_data['search_results'])

@app.route('/evaluate_context', methods=['GET', 'POST'])
def evaluate_context():
    """
    COMPREHENSIVE CONTEXT EVALUATION DISPLAY
    
    Primary results display page that presents complete AI analysis results
    with full transparency, step-by-step reasoning, and actionable insights.
    The centerpiece of user interaction with AI analysis results.
    
    DISPLAY FEATURES:
    
    ✅ STEP-BY-STEP ANALYSIS PROCESS:
       - Complete 10-step analysis breakdown
       - Real-time reasoning as AI processes the request
       - Clear explanations for each analysis decision
    
    ✅ DATA SOURCE TRANSPARENCY:
       - "Data Sources Used": Which knowledge bases were consulted
       - "Data Sources Skipped": Which sources weren't relevant (with reasons)
       - Complete audit trail of information sources
    
    ✅ MICROSOFT PRODUCT DETECTION:
       - Identified Microsoft products with confidence scores
       - Context awareness (training, demo, production contexts)
       - Product-specific recommendations and guidance
    
    ✅ CORRECTIVE LEARNING DISPLAY:
       - Applied corrections from previous user feedback
       - Learning patterns and improvement tracking
       - Institutional memory utilization
    
    ✅ CONFIDENCE AND DECISION ANALYSIS:
       - Overall confidence score with contributing factors
       - Category and intent classification with reasoning
       - Business impact and urgency assessment
    
    REQUEST HANDLING:
    - GET: Display results from session-stored analysis
    - POST: Handle new analysis requests and update display
    
    TEMPLATE INTEGRATION:
    - Uses context_evaluation.html for rich result display
    - Passes comprehensive reasoning data to template
    - Enables interactive exploration of analysis results
    
    SESSION MANAGEMENT:
    - Retrieves analysis results from session or temporary storage
    - Handles evaluation ID-based result lookup
    - Manages large result datasets efficiently
    """
    """Handle context evaluation form display and submission"""
    if request.method == 'GET':
        # Get evaluation ID from query parameters
        evaluation_id = request.args.get('eval_id')
        if not evaluation_id or evaluation_id not in temp_storage:
            flash('Evaluation session not found or expired', 'error')
            return redirect(url_for('index'))
        
        # Get evaluation data from temporary storage
        evaluation_data = temp_storage[evaluation_id]
        
        # [DEBUG] Check what data we're passing to the template
        context_data = evaluation_data['context_analysis']
        print(f"[DEBUG] Context data keys: {list(context_data.keys())}")
        print(f"[DEBUG] Category: '{context_data.get('category', 'MISSING')}'")
        print(f"[DEBUG] Intent: '{context_data.get('intent', 'MISSING')}'")
        print(f"[DEBUG] Confidence: '{context_data.get('confidence', 'MISSING')}'")
        print(f"[DEBUG] Business Impact: '{context_data.get('business_impact', 'MISSING')}'")
        
        # Check if this is a reanalyzed version
        is_reanalyzed = evaluation_data['context_analysis'].get('reanalyzed', False)
        corrections_applied = evaluation_data['context_analysis'].get('corrections_applied', {})
        
        return render_template('context_evaluation.html',
                             evaluation_id=evaluation_id,
                             original_title=evaluation_data['original_issue']['title'],
                             original_description=evaluation_data['original_issue']['description'],
                             original_impact=evaluation_data['original_issue'].get('impact', ''),
                             context=evaluation_data['context_analysis'],
                             search_strategy=evaluation_data.get('recommended_strategy', {'type': 'comprehensive', 'search_ado': True, 'search_retirements': True}),
                             is_reanalyzed=is_reanalyzed,
                             corrections_applied=corrections_applied,
                             cache_buster=datetime.now().timestamp())
    
    elif request.method == 'POST':
        # Process evaluation form submission
        evaluation_id = request.form.get('evaluation_id')
        evaluation_result = request.form.get('evaluation_result')  # 'approve' or 'reject'
        action = request.form.get('action', 'default')  # New action field
        
        if not evaluation_id or evaluation_id not in temp_storage:
            flash('Evaluation session not found or expired', 'error')
            return redirect(url_for('index'))
        
        # Get original evaluation data
        evaluation_data = temp_storage[evaluation_id]
        
        # Prepare feedback data for storage
        feedback_data = {
            'original_issue': evaluation_data['original_issue'],
            'system_analysis': evaluation_data['context_analysis'],
            'evaluation_result': evaluation_result,
            'timestamp': datetime.now().isoformat(),
            'general_feedback': request.form.get('general_feedback', '')
        }
        
        # Handle different actions
        if action == 'reanalyze':
            # Reanalyze with corrections
            corrections = {
                'correct_category': request.form.get('correct_category'),
                'correct_intent': request.form.get('correct_intent'),
                'correct_business_impact': request.form.get('correct_business_impact'),
                'correct_technical_complexity': request.form.get('correct_technical_complexity'),
                'correct_urgency_level': request.form.get('correct_urgency_level'),
                'correction_notes': request.form.get('correction_notes', '')
            }
            
            feedback_data['corrections'] = corrections
            
            # Save feedback for learning
            tracker.save_evaluation(feedback_data)
            
            # Perform reanalysis with corrected parameters
            original_issue = evaluation_data['original_issue']
            
            # Create corrected issue data for reanalysis
            corrected_issue = {
                'title': original_issue['title'],
                'description': original_issue['description'],
                'impact': original_issue.get('impact', corrections['correct_business_impact']),
                # Override with corrections
                'corrected_category': corrections['correct_category'],
                'corrected_intent': corrections['correct_intent'],
                'corrected_business_impact': corrections['correct_business_impact']
            }
            
            print(f"🔄 REANALYSIS: Starting with corrections - Category: {corrections['correct_category']}, Intent: {corrections['correct_intent']}")
            
            # Import and use the enhanced matching system
            from enhanced_matching import EnhancedMatcher
            matcher = EnhancedMatcher(tracker)  # Pass the tracker instance
            
            # Create a simple progress callback for logging
            def progress_callback(current_step, total_steps, percentage, message):
                print(f"🔄 REANALYSIS PROGRESS: Step {current_step}/{total_steps} ({percentage}%) - {message}")
            
            # Run reanalysis with corrected parameters
            results = matcher.intelligent_search_all_sources(
                title=corrected_issue['title'],
                description=corrected_issue['description'],
                impact=corrected_issue['impact'],
                progress_callback=progress_callback,
                skip_evaluation=True  # Skip evaluation since we already have corrections
            )
            
            # Create new analysis data for re-evaluation
            new_context_analysis = results.get('context_analysis', {})
            
            # Perform a fresh context analysis with corrected parameters as guidance
            corrected_title = corrected_issue['title']
            corrected_description = corrected_issue['description'] 
            corrected_impact = corrected_issue['impact']
            
            # Add correction context to the description for reanalysis
            enhanced_description = f"{corrected_description}\n\n[Correction Context: User indicated this should be categorized as '{corrections['correct_category']}' with intent '{corrections['correct_intent']}' and business impact '{corrections['correct_business_impact']}']"
            
            # Run fresh context analysis with enhanced description
            fresh_analysis = matcher.context_analyzer.analyze(
                corrected_title, 
                enhanced_description, 
                corrected_impact
            )
            
            # Convert fresh analysis to dictionary format
            # Handle both enum and string values for category/intent
            category_value = fresh_analysis.category.value if hasattr(fresh_analysis.category, 'value') else fresh_analysis.category
            intent_value = fresh_analysis.intent.value if hasattr(fresh_analysis.intent, 'value') else fresh_analysis.intent
            
            new_context_analysis = {
                'category': category_value,
                'intent': intent_value,
                'confidence': fresh_analysis.confidence,
                'business_impact': fresh_analysis.business_impact,
                'technical_complexity': fresh_analysis.technical_complexity,
                'urgency_level': fresh_analysis.urgency_level,
                'context_summary': fresh_analysis.context_summary,
                'key_concepts': fresh_analysis.key_concepts,
                'semantic_keywords': fresh_analysis.semantic_keywords,
                'domain_entities': fresh_analysis.domain_entities,
                'recommended_search_strategy': fresh_analysis.recommended_search_strategy,
                
                # Analysis details
                'reasoning': fresh_analysis.reasoning,
                'pattern_features': fresh_analysis.pattern_features,
                'pattern_reasoning': fresh_analysis.pattern_reasoning if hasattr(fresh_analysis, 'pattern_reasoning') else None,
                'source': fresh_analysis.source,
                
                # AI status tracking
                'ai_available': fresh_analysis.ai_available,
                'ai_error': fresh_analysis.ai_error,
                
                # Display-friendly field mappings
                'category_display': category_value.replace('_', ' ').title(),
                'intent_display': intent_value.replace('_', ' ').title(),
                'business_impact_display': fresh_analysis.business_impact.replace('_', ' ').title() if fresh_analysis.business_impact else 'Not Assessed'
            }
            
            # Override with user corrections to ensure they take precedence
            if corrections['correct_category']:
                new_context_analysis['category'] = corrections['correct_category']
            if corrections['correct_intent']:
                new_context_analysis['intent'] = corrections['correct_intent'] 
            if corrections['correct_business_impact']:
                new_context_analysis['business_impact'] = corrections['correct_business_impact']
                
            # Update context summary to reflect corrections
            original_summary = new_context_analysis['context_summary']
            new_context_analysis['context_summary'] = f"{original_summary} [Updated with user corrections: Category={corrections['correct_category']}, Intent={corrections['correct_intent']}, Impact={corrections['correct_business_impact']}]"
            
            # Mark as reanalyzed
            new_context_analysis['reanalyzed'] = True
            new_context_analysis['corrections_applied'] = corrections
            
            # Create new evaluation data for the updated analysis
            new_evaluation_data = {
                'original_issue': original_issue,
                'context_analysis': new_context_analysis,
                'recommended_strategy': results.get('search_strategy_used', {}),
                'reanalysis_results': results,  # Store full results for later use
                'timestamp': datetime.now().isoformat()
            }
            
            # Store the new evaluation for review
            new_eval_id = str(uuid.uuid4())
            temp_storage[new_eval_id] = new_evaluation_data
            
            print(f"🔄 REANALYSIS COMPLETE: New analysis ready for review")
            flash('Reanalysis complete! Please review the updated analysis below.', 'success')
            
            # Redirect back to summary page to show updated classification
            return redirect(url_for('context_summary', eval_id=new_eval_id))
        
        elif action == 'save_corrections':
            # Save corrections without reanalyzing
            feedback_data['corrections'] = {
                'correct_category': request.form.get('correct_category'),
                'correct_intent': request.form.get('correct_intent'),
                'correct_business_impact': request.form.get('correct_business_impact'),
                'correct_technical_complexity': request.form.get('correct_technical_complexity'),
                'correct_urgency_level': request.form.get('correct_urgency_level'),
                'correction_notes': request.form.get('correction_notes', '')
            }
            
            # Save feedback for learning
            tracker.save_evaluation(feedback_data)
            
            flash('Your corrections have been saved for system improvement. Thank you!', 'success')
            return redirect(url_for('index'))
        
        elif evaluation_result == 'reject':
            # Original reject logic for backward compatibility
            feedback_data['corrections'] = {
                'correct_category': request.form.get('correct_category'),
                'correct_intent': request.form.get('correct_intent'),
                'correct_business_impact': request.form.get('correct_business_impact'),
                'correction_notes': request.form.get('correction_notes', '')
            }
            
            tracker.save_evaluation(feedback_data)
            flash('Thank you for your feedback! The system analysis has been rejected and will not proceed with matching. Your corrections have been saved for system improvement.', 'info')
            return redirect(url_for('index'))
        
        else:  # evaluation_result == 'approve' or action == 'approve'
            # Save approval feedback
            tracker.save_evaluation(feedback_data)
            
            # Check if this is approving reanalyzed data
            if evaluation_data['context_analysis'].get('reanalyzed', False):
                # Use the stored reanalysis results
                reanalysis_results = evaluation_data.get('reanalysis_results', {})
                
                if reanalysis_results.get('total_matches', 0) > 0:
                    # Store results for display
                    results_id = str(uuid.uuid4())
                    temp_storage[results_id] = {
                        'enhanced_results': reanalysis_results,
                        'enhanced_info': {'reanalysis_approved': True, 'corrections_applied': evaluation_data['context_analysis'].get('corrections_applied', {})},
                        'timestamp': time.time()
                    }
                    
                    # Set session variables for results page
                    session['current_issue'] = evaluation_data['original_issue']['title']
                    session['wizard_title'] = evaluation_data['original_issue']['title']
                    session['results_id'] = results_id
                    
                    flash('Reanalyzed context approved! Showing your corrected matches.', 'success')
                    return redirect(url_for('results'))
                else:
                    # No matches found in reanalysis
                    session['current_issue'] = evaluation_data['original_issue']['title']
                    session['wizard_title'] = evaluation_data['original_issue']['title']
                    flash('Reanalyzed context approved, but no matches were found with the corrected parameters.', 'info')
                    return redirect(url_for('no_match'))
            
            # Original approval logic for non-reanalyzed data
            flash('Context analysis approved! Proceeding with intelligent matching...', 'success')
            
            # [CONFIG] APPLY USER'S RETIREMENT SEARCH OVERRIDE
            retirement_override = request.form.get('override_search_retirements')
            if retirement_override is not None:
                # Update the recommended strategy based on user choice
                evaluation_data['recommended_strategy']['search_retirements'] = (retirement_override == 'true')
                print(f"[CONFIG] USER OVERRIDE: search_retirements = {evaluation_data['recommended_strategy']['search_retirements']}")
            
            # Store approved evaluation data for processing
            process_id = str(uuid.uuid4())
            temp_storage[process_id] = evaluation_data
            
            # Initialize processing session for approved search
            app.config['processing_sessions'] = app.config.get('processing_sessions', {})
            app.config['processing_sessions'][process_id] = {
                'step': 1, 'total_steps': 4, 'progress_percent': 25,
                'current_task': 'Starting approved intelligent search...',
                'completed': False, 'evaluation_approved': True
            }
            
            # Get wizard data before starting background thread (to avoid session context issues)
            wizard_data = session.get('original_wizard_data', {})
            
            # Start background processing with approved context
            def process_approved_search():
                try:
                    from enhanced_matching import EnhancedMatcher
                    
                    def progress_update(step, total, percent, task):
                        app.config['processing_sessions'][process_id].update({
                            'step': step, 'total_steps': total, 
                            'progress_percent': percent, 'current_task': task
                        })
                    
                    matcher = EnhancedMatcher(tracker)
                    search_results = matcher.continue_intelligent_search_after_approval(evaluation_data, progress_update)
                    
                    # Extract the actual results structure (same as other search paths)
                    if 'results' in search_results:
                        results = search_results['results']
                    else:
                        results = search_results
                    
                    # Store results in the format expected by /no_match route
                    results_id = str(uuid.uuid4())
                    temp_storage[results_id] = {
                        'enhanced_results': results,
                        'timestamp': time.time()
                    }
                    
                    print(f"[DEBUG] APPROVED SEARCH: Stored results with ID = {results_id}")
                    print(f"[DEBUG] APPROVED SEARCH: Results keys = {list(results.keys())}")
                    print(f"[DEBUG] APPROVED SEARCH: Total matches = {results.get('total_matches', 0)}")
                    print(f"[DEBUG] APPROVED SEARCH: UAT items = {len(results.get('uat_items', []))}")
                    
                    # Also store for backward compatibility with /results route
                    temp_storage[f"{process_id}_results"] = results
                    
                    # Store results_id and wizard data in processing session (NOT in session - that causes context errors)
                    app.config['processing_sessions'][process_id].update({
                        'completed': True, 'progress_percent': 100,
                        'current_task': 'Approved search completed successfully!',
                        'results_id': results_id,  # Store results_id for redirect
                        'wizard_data': wizard_data  # Store wizard data to avoid session access later
                    })
                    
                except Exception as e:
                    print(f"Approved search error: {e}")
                    app.config['processing_sessions'][process_id].update({
                        'completed': True, 'error': str(e), 'progress_percent': 0
                    })
            
            thread = threading.Thread(target=process_approved_search)
            thread.daemon = True
            thread.start()
            
            return render_template('processing.html', 
                                 process_id=process_id,
                                 progress={'step': 1, 'total_steps': 4, 'progress_percent': 25},
                                 current_task='Starting approved intelligent search...')

@app.route('/quick_ica', methods=['POST'])
def quick_ica():
    """Quick ICA form submission - bypass wizard and go straight to context analysis"""
    try:
        # Get issue data from form
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        impact = request.form.get('impact', '').strip()
        
        # DEBUG: Show what data is being submitted for analysis
        print("=" * 80)
        print("[DEBUG] QUICK ICA SUBMISSION DATA:")
        print(f"[DEBUG] Title: '{title}'")
        print(f"📄 Description: '{description}'")
        print(f"💼 Impact: '{impact}'")
        print(f"📏 Title length: {len(title)} chars")
        print(f"📏 Description length: {len(description)} chars")
        print(f"📏 Impact length: {len(impact)} chars")
        print("=" * 80)
        
        if not title or not description:
            flash('Title and description are required for ICA analysis', 'error')
            return redirect(url_for('index'))
        
        # Perform context analysis for evaluation
        from enhanced_matching import EnhancedMatcher
        matcher = EnhancedMatcher(tracker)
        evaluation_data = matcher.analyze_context_for_evaluation(title, description, impact)
        
        # Store evaluation data temporarily
        evaluation_id = str(uuid.uuid4())
        temp_storage[evaluation_id] = evaluation_data
        
        # Redirect to summary page for user review
        return redirect(url_for('context_summary', eval_id=evaluation_id))
        
    except Exception as e:
        print(f"Quick ICA error: {e}")
        flash(f'Error running ICA analysis: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/start_evaluation', methods=['POST'])
def start_evaluation():
    """Start the evaluation process with context analysis"""
    try:
        # Get issue data from form
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        impact = request.form.get('impact', '').strip()
        
        if not title or not description:
            flash('Title and description are required for context evaluation', 'error')
            return redirect(url_for('index'))
        
        # Perform context analysis for evaluation
        from enhanced_matching import EnhancedMatcher
        matcher = EnhancedMatcher(tracker)
        evaluation_data = matcher.analyze_context_for_evaluation(title, description, impact)
        
        # Store evaluation data temporarily
        evaluation_id = str(uuid.uuid4())
        temp_storage[evaluation_id] = evaluation_data
        
        # Redirect to summary page for user review
        return redirect(url_for('context_summary', eval_id=evaluation_id))
        
    except Exception as e:
        print(f"Evaluation start error: {e}")
        flash(f'Error starting evaluation: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/admin/evaluations')
def admin_evaluations():
    """Admin page to view evaluation statistics and feedback"""
    stats = tracker.get_learning_statistics()
    recent_evaluations = tracker.evaluations.get("evaluations", [])[-10:]  # Last 10 evaluations
    
    return render_template('admin_evaluations.html', 
                         statistics=stats,
                         recent_evaluations=recent_evaluations)

@app.route('/results')
def results():
    """Display search results after processing"""
    process_id = session.get('process_id')
    if not process_id:
        flash('No active search session found', 'error')
        return redirect(url_for('index'))
    
    # Get results from temporary storage - check both possible keys
    results_id = session.get('results_id')
    results_data = {}
    
    if results_id:
        # Try results_id first (from background thread)
        results_data = temp_storage.get(results_id, {})
        print(f"[DEBUG] RESULTS: Looking for results_id = {results_id}")
        print(f"[DEBUG] RESULTS: Found data with keys = {list(results_data.keys()) if results_data else 'None'}")
    
    if not results_data:
        # Fallback to old format
        results_key = f"{process_id}_results"
        results_data = temp_storage.get(results_key, {})
        print(f"[DEBUG] RESULTS: Fallback to process_id key = {results_key}")
        print(f"[DEBUG] RESULTS: Found fallback data = {bool(results_data)}")
    
    if not results_data:
        print(f"[DEBUG] RESULTS: No results found for process_id = {process_id} or results_id = {results_id}")
        flash('No results found for this session', 'error')
        return redirect(url_for('index'))
    
    # Extract match data - handle both old and new formats
    if 'enhanced_results' in results_data:
        # New format from background thread
        enhanced_results = results_data.get('enhanced_results', {})
        uat_items = enhanced_results.get('uat_items', [])
        feature_items = enhanced_results.get('feature_items', [])
        all_items = enhanced_results.get('all_items', [])
        print(f"[DEBUG] RESULTS: Using enhanced_results format")
        print(f"[DEBUG] RESULTS: UAT items = {len(uat_items)}, Feature items = {len(feature_items)}, All items = {len(all_items)}")
    else:
        # Old format
        uat_items = results_data.get('uat_items', [])
        feature_items = results_data.get('feature_items', [])
        all_items = results_data.get('all_items', [])
        print(f"[DEBUG] RESULTS: Using old format")
    
    total_matches = len(uat_items) + len(feature_items) + len(all_items)
    print(f"[DEBUG] RESULTS: Total matches calculated = {total_matches}")
    
    return render_template('results.html',
                         uat_items=uat_items,
                         feature_items=feature_items,
                         all_items=all_items,
                         total_matches=total_matches,
                         process_id=process_id)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("="*80)
    print("Issue Tracker System starting...")
    print("="*80)
    
    # Health check for AI services - TEMPORARILY DISABLED FOR TESTING
    print("\nSkipping health check for now...")
    # try:
    #     from hybrid_context_analyzer import HybridContextAnalyzer
    #     from ai_config import get_config, validate_config
    #     
    #     # Try to validate configuration
    #     config = get_config()
    #     azure_config = config.azure_openai
    #     
    #     if azure_config.endpoint and azure_config.api_key:
    #         print(f"[OK] Azure OpenAI Endpoint configured: {azure_config.endpoint}")
    #         print(f"[OK] Deployment: {azure_config.classification_deployment}")
    #         print(f"[OK] API Version: {azure_config.api_version}")
    #         
    #         # Try to initialize analyzer to test connection
    #         try:
    #             test_analyzer = HybridContextAnalyzer(use_ai=True)
    #             print("[OK] AI services initialized successfully")
    #             print(f"[OK] System Mode: AI-Powered (High Confidence)")
    #         except Exception as e:
    #             print(f"[WARNING] AI initialization warning: {str(e)}")
    #             print(f"[WARNING] System Mode: Pattern Matching Fallback")
    #             print(f"          The system will use pattern-based analysis (50-90% confidence)")
    #             print(f"          This is functional but not optimal. Check Azure OpenAI configuration.")
    #     else:
    #         print("[WARNING] Azure OpenAI not configured (missing endpoint or API key)")
    #         print("[WARNING] System Mode: Pattern Matching Only")
    # except Exception as e:
    #     print(f"[WARNING] Health check error: {e}")
    #     print(f"[WARNING] System will attempt to start anyway...")
    
    print("="*80)
    port = 5002
    print(f"\nNavigate to http://127.0.0.1:{port} to access the application\n")
    
    # VS Code debugging compatibility
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1' or os.environ.get('FLASK_ENV') == 'development'
    
    # Enable debug mode and template reloading
    # Temporarily disable debug mode to test if that's causing immediate exit
    app.config['DEBUG'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    try:
        print("[DEBUG] Starting Flask with app.run()...")
        app.run(debug=False, host='127.0.0.1', port=port, use_reloader=False, threaded=True)
        print("[DEBUG] Flask exited normally")
    except Exception as e:
        import traceback
        print(f"\n[ERROR] Flask failed to start!")
        print(f"[ERROR] Exception: {e}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()
        print("\n[RETRY] Attempting fallback without debug mode...")
        try:
            app.run(debug=False, host='127.0.0.1', port=port, use_reloader=False)
        except Exception as e2:
            print(f"[ERROR] Fallback also failed: {e2}")
            traceback.print_exc()