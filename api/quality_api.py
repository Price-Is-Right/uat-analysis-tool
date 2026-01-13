"""
Quality Analysis API
====================

Endpoint for analyzing input quality and completeness.
Used by Teams bot to validate user input before proceeding.

POST /api/v1/analyze/quality
Request: {title: str, description: str, impact: str}
Response: {score: int, suggestions: list, completeness: dict}
"""

from flask import request, jsonify
from . import api_bp
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@api_bp.route('/analyze/quality', methods=['POST'])
def analyze_quality():
    """
    Analyze input quality and provide improvement suggestions.
    
    This uses the AIAnalyzer.analyze_completeness logic to validate
    that the user has provided sufficient information for accurate analysis.
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
        if not title:
            return jsonify({
                'error': 'Title is required',
                'status': 'error'
            }), 400
        
        if not description:
            return jsonify({
                'error': 'Description is required',
                'status': 'error'
            }), 400
        
        # Import AIAnalyzer
        from enhanced_matching import AIAnalyzer
        
        # Create analyzer instance
        analyzer = AIAnalyzer()
        
        # Perform quality analysis
        quality_result = analyzer.analyze_completeness(title, description, impact)
        
        # Return structured response
        return jsonify({
            'status': 'success',
            'score': quality_result['completeness_score'],
            'is_complete': quality_result['is_complete'],
            'needs_improvement': quality_result['needs_improvement'],
            'suggestions': quality_result['suggestions'],
            'issues': quality_result['issues'],
            'garbage_detected': quality_result['garbage_detected'],
            'garbage_details': quality_result['garbage_details']
        }), 200
        
    except Exception as e:
        print(f"[API ERROR] Quality analysis failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': f'Quality analysis failed: {str(e)}',
            'status': 'error'
        }), 500
