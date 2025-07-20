# main.py
from dotenv import load_dotenv
import os
from pathlib import Path
import logging

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Load .env file with graceful fallback
def load_environment_variables():
    """
    Load environment variables from .env file with graceful fallback.
    
    Tries to load from multiple possible locations:
    1. Parent directory (project root)
    2. Current directory
    3. Falls back gracefully if no .env file found
    """
    # Try multiple possible .env file locations
    possible_paths = [
        Path(__file__).resolve().parent.parent / ".env",  # Parent directory (project root)
        Path(__file__).resolve().parent / ".env",         # Current directory
        Path.cwd() / ".env",                              # Current working directory
    ]
    
    env_loaded = False
    for dotenv_path in possible_paths:
        if dotenv_path.exists():
            try:
                load_dotenv(dotenv_path=dotenv_path)
                logger.info(f"✅ Environment variables loaded from: {dotenv_path}")
                env_loaded = True
                break
            except Exception as e:
                logger.warning(f"⚠️ Failed to load .env from {dotenv_path}: {e}")
                continue
    
    if not env_loaded:
        logger.warning("⚠️ No .env file found. Using system environment variables only.")
        logger.info("💡 To configure API keys, create a .env file in the project root with:")
        logger.info("   OPENAI_API_KEY=your_openai_api_key_here")
        logger.info("   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here")
    
    # Log environment status
    api_keys_status = {
        "OPENAI_API_KEY": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing",
        "GOOGLE_MAPS_API_KEY": "✅ Set" if os.getenv("GOOGLE_MAPS_API_KEY") else "❌ Missing",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "DEBUG": os.getenv("DEBUG", "true")
    }
    
    logger.info("🔧 Environment configuration:")
    for key, status in api_keys_status.items():
        logger.info(f"   {key}: {status}")

# Load environment variables
load_environment_variables()


import logging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import re
import uuid
from fastapi.openapi.docs import get_swagger_ui_html
import json
from fastapi.responses import HTMLResponse

from api.v1.router import api_router
from schemas.responses import ApiResponse
from core.usage_metrics import log_usage

app = FastAPI()

# Enable CORS for browser-based testing and Swagger UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to your frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Logging Config ---
# (Already configured at the top of the file)

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
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure appropriately for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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
        api_version="v1",
        error=None,
        detail=None,
        status_code=None,
        error_code=None,
        trace_id=None,
        support_link=None
    )

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors with structured error information.
    """
    # Get trace_id from request state if available
    trace_id = getattr(request.state, 'trace_id', None)
    
    # Log the full exception for debugging
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Determine if this is a known error type
    if hasattr(exc, 'error_code'):
        # This is a structured exception from our error handlers
        error_code = getattr(exc, 'error_code', "ERR_UNKNOWN")
        detail = getattr(exc, 'detail', str(exc))
        status_code = getattr(exc, 'status_code', 500)
        support_link = getattr(exc, 'support_link', f"https://support.healthymealfinder.com/errors/{error_code}")
    else:
        # Generic unhandled exception
        error_code = "ERR_UNKNOWN"
        detail = "An unexpected error occurred. Please try again later."
        status_code = 500
        support_link = "https://support.healthymealfinder.com/errors/ERR_UNKNOWN"
    
    return JSONResponse(
        status_code=status_code,
        content=ApiResponse(
            success=False,
            data=None,
            message=None,
            error="Internal server error" if status_code == 500 else "Request failed",
            detail=detail,
            status_code=status_code,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version="v1",
            error_code=error_code,
            trace_id=trace_id,
            support_link=support_link
        ).model_dump(),
        headers=getattr(exc, 'headers', {})
    )

# --- 404 Handler ---
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """
    Custom 404 handler with consistent response format.
    """
    # Generate trace_id if not already present
    trace_id = getattr(request.state, 'trace_id', str(uuid.uuid4()))
    
    return JSONResponse(
        status_code=404,
        content=ApiResponse(
            success=False,
            data=None,
            message=None,
            error="Endpoint not found",
            detail=f"The requested endpoint {request.url.path} was not found",
            status_code=404,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version="v1",
            error_code="ERR_ENDPOINT_NOT_FOUND",
            trace_id=trace_id,
            support_link="https://support.healthymealfinder.com/errors/ERR_ENDPOINT_NOT_FOUND"
        ).model_dump()
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
                # Always inject trace_id for error responses
                data["trace_id"] = trace_id
                # Add error_code if not present
                if "error_code" not in data or data["error_code"] is None:
                    data["error_code"] = "ERR_UNKNOWN"
                # Add support_link if not present
                if "support_link" not in data or data["support_link"] is None:
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
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Healthy Meal Finder API Explorer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; }
            h1 { color: #2d7a2d; }
            code, pre { background: #eee; padding: 2px 4px; border-radius: 3px; }
            .section { margin-bottom: 2em; }
        </style>
    </head>
    <body>
        <h1>Healthy Meal Finder API Explorer</h1>
        <div class="section">
            <h2>Getting Started</h2>
            <p>All endpoints require an <b>X-API-Key</b> header. Example: <code>X-API-Key: your_partner_key</code></p>
            <p>Base URL: <code>http://localhost:8000/api/v1</code></p>
        </div>
        <div class="section">
            <h2>Endpoints</h2>
            <ul>
                <li><b>Find Meals</b>: <code>POST /api/v1/meals/find</code> — Get meal recommendations by location and goal.</li>
                <li><b>Freeform Search</b>: <code>POST /api/v1/meals/freeform-search</code> — Search meals with natural language.</li>
                <li><b>Nutrition Estimate</b>: <code>POST /api/v1/nutrition/estimate</code> — Estimate nutrition from a meal description.</li>
                <li><b>Fitness Goals</b>: <code>GET /api/v1/meals/goals</code> — List supported fitness goals.</li>
                <li><b>Health Check</b>: <code>GET /api/v1/health/</code> — Service health status.</li>
            </ul>
        </div>
        <div class="section">
            <h2>Example: Find Meals (curl)</h2>
            <pre><code>curl -X POST http://localhost:8000/api/v1/meals/find \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_partner_key" \
  -d '{
    "lat": 40.7128,
    "lon": -74.0060,
    "goal": "muscle_gain",
    "radius_miles": 5
  }'
</code></pre>
        </div>
        <div class="section">
            <h2>Example: Nutrition Estimate (curl)</h2>
            <pre><code>curl -X POST http://localhost:8000/api/v1/nutrition/estimate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_partner_key" \
  -d '{
    "meal_description": "Grilled chicken with quinoa and veggies",
    "serving_size": "1 serving"
  }'
</code></pre>
        </div>
        <div class="section">
            <h2>More</h2>
            <ul>
                <li>See <a href="/docs">Swagger UI</a> for interactive API docs.</li>
                <li>See <a href="/openapi.json">OpenAPI spec</a> for schema.</li>
            </ul>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)

# Usage logger for partner API tracking
usage_logger = logging.getLogger("usage_logger")
if not usage_logger.handlers:
    handler = logging.FileHandler("usage.log")
    handler.setFormatter(logging.Formatter('%(message)s'))
    usage_logger.addHandler(handler)
    usage_logger.setLevel(logging.INFO)

@app.middleware("http")
async def usage_logging_middleware(request: Request, call_next):
    api_key = request.headers.get("x-api-key", "unknown")
    endpoint = request.url.path
    timestamp = datetime.utcnow().isoformat() + "Z"
    response = await call_next(request)
    status_code = response.status_code
    # --- Rate tracking logic placeholder ---
    # Here you could increment counters, check limits, etc.
    # ---------------------------------------
    usage_logger.info(json.dumps({
        "timestamp": timestamp,
        "api_key": api_key,
        "endpoint": endpoint,
        "status_code": status_code
    }))
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)