# routers/health.py

from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={200: {"description": "Service is healthy"}}
)

@router.get(
    "/",
    summary="Health Check",
    description="""
    Check the health status of the Healthy Meal Finder API.
    
    This endpoint returns basic information about the service status,
    including uptime and version information.
    """,
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "version": "1.0.0",
                        "service": "Healthy Meal Finder API"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Health check endpoint for the API.
    
    Returns:
        Dictionary containing service health information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "service": "Healthy Meal Finder API"
    }

@router.get(
    "/ready",
    summary="Readiness Check",
    description="""
    Check if the service is ready to handle requests.
    
    This endpoint verifies that all required dependencies
    (like external APIs) are available and functioning.
    """,
    responses={
        200: {
            "description": "Service is ready",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ready",
                        "dependencies": {
                            "google_places_api": "connected",
                            "database": "connected"
                        }
                    }
                }
            }
        },
        503: {
            "description": "Service is not ready",
            "content": {
                "application/json": {
                    "example": {
                        "status": "not_ready",
                        "dependencies": {
                            "google_places_api": "disconnected",
                            "database": "connected"
                        }
                    }
                }
            }
        }
    }
)
async def readiness_check():
    """
    Readiness check endpoint for the API.
    
    Returns:
        Dictionary containing service readiness information
    """
    # Check if Google API key is configured
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    dependencies = {
        "google_places_api": "connected" if google_api_key else "disconnected"
    }
    
    is_ready = all(status == "connected" for status in dependencies.values())
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "dependencies": dependencies
    } 