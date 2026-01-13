"""
Context Analysis API
====================

Endpoint for intelligent context analysis of issues.
Uses IntelligentContextAnalyzer to understand category, intent, and domain.

POST /api/v1/analyze/context
Request: {title: str, description: str, impact: str}
Response: {category, intent, confidence, domain_entities, detected_products, reasoning, analysis_steps}
"""

from flask import request, jsonify
from . import api_bp
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@api_bp.route('/analyze/context', methods=['POST'])
def analyze_context():
    """
    Perform comprehensive intelligent context analysis.
    
    Returns complete analysis including category classification, intent detection,
    entity extraction, product detection, and step-by-step reasoning.
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        # Extract fields
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        impact = data.get('impact', '').strip()
        
        # Validate required fields
        if not title or not description:
            return jsonify({
                'error': 'Title and description are required',
                'status': 'error'
            }), 400
        
        # Import context analyzer
        from enhanced_matching import EnhancedMatcher, ProgressTracker
        
        # Create tracker for progress (but we won't use it for API)
        tracker = ProgressTracker()
        
        # Create matcher instance
        matcher = EnhancedMatcher(tracker)
        
        # Perform context analysis
        evaluation_data = matcher.analyze_context_for_evaluation(title, description, impact)
        
        # Extract context analysis from evaluation data
        context_analysis = evaluation_data.get('context_analysis', {})
        
        # Return structured response
        return jsonify({
            'status': 'success',
            'category': context_analysis.get('category'),
            'category_display': context_analysis.get('category_display'),
            'intent': context_analysis.get('intent'),
            'intent_display': context_analysis.get('intent_display'),
            'confidence': context_analysis.get('confidence'),
            'business_impact': context_analysis.get('business_impact'),
            'business_impact_display': context_analysis.get('business_impact_display'),
            'domain_entities': context_analysis.get('domain_entities', {}),
            'detected_products': context_analysis.get('detected_products', []),
            'key_concepts': context_analysis.get('key_concepts', []),
            'technical_complexity': context_analysis.get('technical_complexity'),
            'urgency_level': context_analysis.get('urgency_level'),
            'reasoning': context_analysis.get('reasoning'),
            'pattern_features': context_analysis.get('pattern_features', {}),
            'pattern_reasoning': context_analysis.get('pattern_reasoning'),
            'source': context_analysis.get('source', 'pattern_matching'),
            'ai_available': context_analysis.get('ai_available', False),
            'ai_error': context_analysis.get('ai_error'),
            'timestamp': evaluation_data.get('timestamp')
        }), 200
        
    except Exception as e:
        print(f"[API ERROR] Context analysis failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': f'Context analysis failed: {str(e)}',
            'status': 'error'
        }), 500
