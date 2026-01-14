"""
Context Analysis API
====================

Endpoint for intelligent context analysis of issues.
Uses IntelligentContextAnalyzer to understand category, intent, and domain.

POST /api/v1/analyze/context
Request: {title: str, description: str, impact: str}
Response: {category, intent, confidence, domain_entities, detected_products, reasoning, analysis_steps}
"""

from flask import request, jsonify, current_app
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
        
        # Write debug to file since terminal output isn't showing
        with open('C:/Projects/Hack/debug_context.log', 'a', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"[DEBUG CONTEXT API] REQUEST RECEIVED\n")
            f.write(f"[DEBUG CONTEXT API] Title: {title}\n")
            f.write(f"[DEBUG CONTEXT API] Description: {description[:200]}\n")
            f.write("="*80 + "\n")
            f.flush()
        
        import sys
        sys.stdout.flush()
        print("="*80, flush=True)
        print(f"[DEBUG CONTEXT API] REQUEST RECEIVED", flush=True)
        print(f"[DEBUG CONTEXT API] Title: {title}", flush=True)
        print(f"[DEBUG CONTEXT API] Description: {description[:100]}...", flush=True)
        print("="*80, flush=True)
        sys.stdout.flush()
        
        # Import context analyzer
        from enhanced_matching import EnhancedMatcher, ProgressTracker
        
        # Create tracker for progress (but we won't use it for API)
        tracker = ProgressTracker()
        
        # Create matcher instance
        matcher = EnhancedMatcher(tracker)
        
        # Perform context analysis
        evaluation_data = matcher.analyze_context_for_evaluation(title, description, impact)
        
        # Extract context analysis from evaluation_data
        context_analysis = evaluation_data.get('context_analysis', {})
        
        # Extract detected products from multiple sources
        domain_entities = context_analysis.get('domain_entities', {})
        # pattern_reasoning is inside context_analysis
        pattern_reasoning = context_analysis.get('pattern_reasoning', {})
        detected_products = []
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[DEBUG API {timestamp}] NEW CODE LOADED - domain_entities received: {domain_entities}")
        print(f"[DEBUG API {timestamp}] pattern_reasoning keys: {pattern_reasoning.keys() if pattern_reasoning else 'None'}")
        
        # First, get Microsoft products from pattern_reasoning (these are the official detected products)
        microsoft_products = pattern_reasoning.get('microsoft_products', [])
        print(f"[DEBUG API] microsoft_products from pattern_reasoning: {microsoft_products}")
        
        if microsoft_products:
            # Smart filtering: Prioritize specific variants over generic base products
            # E.g., "Defender for Databases" is more specific than "Microsoft Defender"
            specific_products = []
            generic_products = []
            
            for product in microsoft_products:
                if isinstance(product, dict):
                    product_name = product.get('title', product.get('name', ''))
                    if product_name:
                        # Check if this is a specific variant (contains "for" or has multiple words)
                        name_lower = product_name.lower()
                        if ' for ' in name_lower or ' studio' in name_lower or ' apps' in name_lower:
                            specific_products.append(product_name)
                        else:
                            generic_products.append(product_name)
                elif isinstance(product, str):
                    if ' for ' in product.lower():
                        specific_products.append(product)
                    else:
                        generic_products.append(product)
            
            # If we have specific variants, only use those
            # Otherwise use all products (generic ones)
            if specific_products:
                detected_products.extend(specific_products)
                print(f"[DEBUG API] Using {len(specific_products)} specific product variants")
            else:
                detected_products.extend(generic_products)
                print(f"[DEBUG API] No specific variants, using {len(generic_products)} generic products")
        
        # If no Microsoft products found, fall back to domain_entities
        if not detected_products:
            # Combine services, products, and technologies into detected_products
            for key in ['azure_services', 'services', 'products', 'technologies']:
                if key in domain_entities and isinstance(domain_entities[key], list):
                    print(f"[DEBUG API] Key '{key}' contains: {domain_entities[key]}")
                    detected_products.extend(domain_entities[key])
        
        print(f"[DEBUG API] Combined detected_products: {detected_products}")
        
        # Remove duplicates with smart normalization (handle plurals, case, etc.)
        def normalize_product_name(name):
            """Normalize product name for deduplication"""
            normalized = str(name).lower().strip()
            # Normalize common plural variations
            normalized = normalized.rstrip('s')  # Remove trailing 's' for plural forms
            return normalized
        
        seen = {}  # Map normalized name -> original name
        unique_products = []
        for product in detected_products:
            normalized = normalize_product_name(product)
            if normalized not in seen:
                seen[normalized] = product
                unique_products.append(product)
            else:
                # Keep the longer/more specific version
                existing = seen[normalized]
                if len(str(product)) > len(str(existing)):
                    # Replace with longer version
                    idx = unique_products.index(existing)
                    unique_products[idx] = product
                    seen[normalized] = product
        
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
            'domain_entities': domain_entities,
            'detected_products': unique_products,  # Now populated from domain_entities
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
