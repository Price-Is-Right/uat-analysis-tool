"""
API Module for ICA System v4.0
================================

RESTful API endpoints for Teams Bot integration and external access.

API Version: v1
Base Path: /api/v1/

Endpoints:
- /api/v1/analyze/quality - Quality analysis for input validation
- /api/v1/analyze/context - Intelligent context analysis
- /api/v1/search/resources - Resource search across multiple sources
- /api/v1/ado/search/features - Search TFT features
- /api/v1/ado/search/uats - Search similar UATs
- /api/v1/uat/create - Create UAT work item

Authentication: Not yet implemented (add later if needed)
CORS: Enabled for Teams bot integration
"""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import route modules (will register routes on blueprint)
from . import quality_api
from . import context_api
from . import search_api
from . import ado_api
from . import uat_api

__all__ = ['api_bp']
