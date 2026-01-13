"""
Resource Search API
===================

Endpoint for searching resources across multiple sources.
Uses ResourceSearchService to search Microsoft Learn, alternatives, regions, etc.

POST /api/v1/search/resources
Request: {title, description, category, intent, domain_entities}
Response: {learn_docs, similar_products, regional_options, capacity_guidance, retirement_info}
"""

from flask import request, jsonify
from . import api_bp
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@api_bp.route('/search/resources', methods=['POST'])
def search_resources():
    """
    Search for relevant resources across multiple sources.
    
    Searches Microsoft Learn documentation, similar products, regional availability,
    capacity guidance, and retirement information based on the issue context.
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
        category = data.get('category', '')
        intent = data.get('intent', '')
        domain_entities = data.get('domain_entities', {})
        
        # Validate required fields
        if not title or not description:
            return jsonify({
                'error': 'Title and description are required',
                'status': 'error'
            }), 400
        
        # Import search service
        from search_service import ResourceSearchService
        
        # Create search service instance
        search_service = ResourceSearchService(use_deep_search=False)
        
        # Perform comprehensive search
        search_results = search_service.search_all(
            title=title,
            description=description,
            category=category,
            intent=intent,
            domain_entities=domain_entities
        )
        
        # Convert results to JSON-serializable format
        response = {
            'status': 'success',
            'learn_docs': [
                {
                    'title': doc.title,
                    'url': doc.url,
                    'snippet': doc.snippet,
                    'source': doc.source,
                    'relevance_score': doc.relevance_score
                }
                for doc in search_results.learn_docs
            ],
            'similar_products': search_results.similar_products,
            'regional_options': search_results.regional_options,
            'capacity_guidance': search_results.capacity_guidance,
            'retirement_info': search_results.retirement_info,
            'search_metadata': search_results.search_metadata
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[API ERROR] Resource search failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': f'Resource search failed: {str(e)}',
            'status': 'error'
        }), 500
