# main.py

import logging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import re
import uuid
from fastapi.openapi.docs import get_swagger_ui_html

from api.v1.router import api_router
from schemas.responses import ApiResponse
from core.usage_metrics import log_usage

# --- Logging Config ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Healthy Meal Finder API...")
    yield
    # Shutdown
    logger.info("Shutting down Healthy Meal Finder API...")

# --- FastAPI App ---
app = FastAPI(
    title="Healthy Meal Finder API",
    description="""
    # Healthy Meal Finder API
    
    A comprehensive API for finding healthy meal recommendations based on location and fitness goals.
    Built for partner consumption with clean response formatting and comprehensive documentation.
    
    ## Features
    
    - **Location-based search**: Find restaurants near your location
    - **Fitness goal matching**: Get meals tailored to your fitness goals
    - **Nutritional analysis**: Detailed nutritional information for each meal
    - **Smart scoring**: Meals are scored based on how well they match your goals
    - **Partner-friendly**: Clean response formatting with consistent structure
    - **Versioned API**: All endpoints under `/api/v1/` for easy versioning
    
    ## Supported Fitness Goals
    
    - **Muscle Gain**: High protein, moderate calories for muscle building
    - **Weight Loss**: Lower calories, moderate protein for weight loss  
    - **Keto**: Low carbs, high fat for ketosis
    - **Balanced**: General healthy eating guidelines
    
    ## API Structure
    
    All endpoints are versioned under `/api/v1/`:
    
    - **Meals**: `/api/v1/meals/*` - Meal recommendations and fitness goals
    - **Health**: `/api/v1/health/*` - Service health and status checks
    
    ## Response Format
    
    All responses follow a consistent format:
    
    ```json
    {
      "success": true,
      "data": { ... },
      "message": "Operation completed successfully",
      "timestamp": "2024-01-15T10:30:00Z",
      "api_version": "v1"
    }
    ```
    
    ## Getting Started
    
    1. Use the `/api/v1/meals/find` endpoint to search for meals
    2. Provide your location coordinates and fitness goal
    3. Get personalized meal recommendations with nutritional details
    
    ## API Documentation
    
    - Interactive API docs: `/docs`
    - Alternative docs: `/redoc`
    - OpenAPI schema: `/openapi.json`
    """,
    version="1.0.0",
    contact={
        "name": "Healthy Meal Finder API Support",
        "email": "support@healthymealfinder.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Routers ---
app.include_router(api_router)

# --- Root Endpoint ---
@app.get(
    "/",
    summary="API Root",
    description="""
    Root endpoint providing basic API information and links to documentation.
    """,
    responses={
        200: {
            "description": "API information",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "message": "Healthy Meal Finder API",
                            "version": "1.0.0",
                            "docs_url": "/docs",
                            "endpoints": {
                                "find_meals": "/api/v1/meals/find",
                                "fitness_goals": "/api/v1/meals/goals",
                                "nutrition_rules": "/api/v1/meals/nutrition-rules/{goal}",
                                "health_check": "/api/v1/health/",
                                "readiness": "/api/v1/health/ready",
                                "status": "/api/v1/health/status"
                            }
                        },
                        "message": "API information retrieved successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        ApiResponse with API information and available endpoints
    """
    return ApiResponse(
        success=True,
        data={
            "message": "Healthy Meal Finder API",
            "version": "1.0.0",
            "docs_url": "/docs",
            "endpoints": {
                "find_meals": "/api/v1/meals/find",
                "fitness_goals": "/api/v1/meals/goals",
                "nutrition_rules": "/api/v1/meals/nutrition-rules/{goal}",
                "health_check": "/api/v1/health/",
                "readiness": "/api/v1/health/ready",
                "status": "/api/v1/health/status"
            }
        },
        message="API information retrieved successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version="v1"
    )

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            success=False,
            error="Internal server error",
            detail="An unexpected error occurred",
            status_code=500,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version="v1"
        ).dict()
    )

# --- 404 Handler ---
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """
    Custom 404 handler with consistent response format.
    """
    return JSONResponse(
        status_code=404,
        content=ApiResponse(
            success=False,
            error="Endpoint not found",
            detail=f"The requested endpoint {request.url.path} was not found",
            status_code=404,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version="v1"
        ).dict()
    )

@app.middleware("http")
async def inject_api_version_middleware(request: Request, call_next):
    response = await call_next(request)
    # Only inject for JSON responses
    if response.headers.get("content-type", "").startswith("application/json"):
        # Try to extract version from path
        match = re.match(r"/api/(v\d+)", request.url.path)
        api_version = match.group(1) if match else None
        if api_version:
            # Read/parse the response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            import json
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    data["api_version"] = api_version
                    return JSONResponse(content=data, status_code=response.status_code, headers=dict(response.headers))
            except Exception:
                pass
            # If parsing fails, return original response
            return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type="application/json")
    return response

@app.middleware("http")
async def usage_metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    api_key = request.headers.get("x-api-key", "unknown")
    endpoint = request.url.path
    log_usage(api_key, endpoint)
    return response

@app.middleware("http")
async def add_trace_id_middleware(request: Request, call_next):
    # Generate a unique trace_id for each request
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    # Inject trace_id into JSON error responses if not present
    if response.headers.get("content-type", "").startswith("application/json"):
        import json
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        try:
            data = json.loads(body)
            if isinstance(data, dict) and (data.get("success") is False or data.get("error")):
                data.setdefault("trace_id", trace_id)
                # Optionally add a support link and error_code if not present
                if "error_code" not in data:
                    data["error_code"] = "ERR_UNKNOWN"
                if "support_link" not in data:
                    data["support_link"] = f"https://support.healthymealfinder.com/errors/{data['error_code']}"
                from fastapi.responses import JSONResponse
                return JSONResponse(content=data, status_code=response.status_code, headers=dict(response.headers))
        except Exception:
            pass
        from fastapi import Response
        return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type="application/json")
    return response

@app.get("/explorer", include_in_schema=False)
def explorer():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Healthy Meal Finder API Explorer",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)