"""
GCS API Gateway
Central routing layer for all GCS microservices
Phase 3: API Gateway Development
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import logging
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.azure')

# Application Insights setup using Azure Monitor OpenTelemetry
APP_INSIGHTS_CONNECTION_STRING = os.getenv('AZURE_APP_INSIGHTS_CONNECTION_STRING')

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Add Application Insights if configured
if APP_INSIGHTS_CONNECTION_STRING:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        
        # Configure Azure Monitor
        configure_azure_monitor(connection_string=APP_INSIGHTS_CONNECTION_STRING)
        logger.info("✅ Application Insights enabled - telemetry will be sent to Azure")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize Application Insights: {e}")
        logger.info("Continuing with console logging only")
else:
    logger.warning("⚠️  Application Insights not configured - using console logging only")

# Initialize FastAPI
app = FastAPI(
    title="GCS API Gateway",
    description="Global Customer Support - Unified Action Tracker API Gateway",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Request tracking middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with correlation ID for tracing"""
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    start_time = datetime.utcnow()
    
    # Log request
    client_host = request.client.host if request.client else "unknown"
    logger.info(
        "Request started",
        extra={
            "custom_dimensions": {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_host,
            }
        }
    )
    
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "custom_dimensions": {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": duration,
            }
        }
    )
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "gcs-api-gateway"
    }

@app.get("/api/info")
async def api_info():
    """API information and available routes"""
    return {
        "name": "GCS API Gateway",
        "version": "1.0.0",
        "description": "Global Customer Support - Unified Action Tracker",
        "routes": {
            "search": "/api/search",
            "analyze": "/api/analyze",
            "matching": "/api/matching",
            "uat": "/api/uat",
            "context": "/api/context",
            "quality": "/api/quality",
            "ado": "/api/ado"
        },
        "status": "Phase 6 - Enhanced Matching Microservice"
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with logging"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "custom_dimensions": {
                "correlation_id": correlation_id,
                "path": request.url.path,
                "error": str(exc),
                "error_type": type(exc).__name__
            }
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "message": str(exc) if os.getenv('DEBUG') else "An error occurred"
        }
    )

# Import route modules
from gateway.routes import search, analyze, uat, context, quality, ado, matching

# Register route blueprints
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(uat.router, prefix="/api/uat", tags=["UAT Management"])
app.include_router(context.router, prefix="/api/context", tags=["Context"])
app.include_router(quality.router, prefix="/api/quality", tags=["Quality"])
app.include_router(ado.router, prefix="/api/ado", tags=["Azure DevOps"])
app.include_router(matching.router, prefix="/api/matching", tags=["Enhanced Matching"])

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    host = os.getenv("API_GATEWAY_HOST", "0.0.0.0")
    port = int(os.getenv("API_GATEWAY_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting GCS API Gateway on {host}:{port}")
    
    uvicorn.run(
        "api_gateway:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
