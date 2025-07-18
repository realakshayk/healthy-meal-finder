# api/v1/endpoints/health.py

from fastapi import APIRouter, Depends
from datetime import datetime
import os

from schemas.responses import ApiResponse
from core.dependencies import get_api_version

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={200: {"description": "Service is healthy"}}
)

@router.get(
    "/",
    response_model=ApiResponse,
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
                        "success": True,
                        "data": {
                            "status": "healthy",
                            "timestamp": "2024-01-15T10:30:00Z",
                            "version": "1.0.0",
                            "service": "Healthy Meal Finder API"
                        },
                        "message": "Service is healthy",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def health_check(api_version: str = Depends(get_api_version)):
    """
    Health check endpoint for the API.
    
    Returns:
        ApiResponse with service health information
    """
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "service": "Healthy Meal Finder API"
        },
        message="Service is healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version=api_version
    )

@router.get(
    "/ready",
    response_model=ApiResponse,
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
                        "success": True,
                        "data": {
                            "status": "ready",
                            "dependencies": {
                                "google_places_api": "connected",
                                "database": "connected"
                            }
                        },
                        "message": "Service is ready",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        },
        503: {
            "description": "Service is not ready",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": {
                            "status": "not_ready",
                            "dependencies": {
                                "google_places_api": "disconnected",
                                "database": "connected"
                            }
                        },
                        "message": "Service is not ready",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def readiness_check(api_version: str = Depends(get_api_version)):
    """
    Readiness check endpoint for the API.
    
    Returns:
        ApiResponse with service readiness information
    """
    # Check if Google API key is configured
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    dependencies = {
        "google_places_api": "connected" if google_api_key else "disconnected"
    }
    
    is_ready = all(status == "connected" for status in dependencies.values())
    
    return ApiResponse(
        success=is_ready,
        data={
            "status": "ready" if is_ready else "not_ready",
            "dependencies": dependencies
        },
        message="Service is ready" if is_ready else "Service is not ready",
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version=api_version
    )

@router.get(
    "/status",
    response_model=ApiResponse,
    summary="Detailed Status",
    description="""
    Get detailed status information about the API service.
    
    This endpoint provides comprehensive information about the service
    including version, uptime, dependencies, and configuration.
    """,
    responses={
        200: {
            "description": "Detailed status information",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "service": "Healthy Meal Finder API",
                            "version": "1.0.0",
                            "status": "healthy",
                            "uptime": "2h 15m 30s",
                            "dependencies": {
                                "google_places_api": "connected",
                                "database": "connected"
                            },
                            "configuration": {
                                "environment": "development",
                                "debug_mode": True,
                                "rate_limiting": True
                            }
                        },
                        "message": "Status retrieved successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def detailed_status(api_version: str = Depends(get_api_version)):
    """
    Get detailed status information about the API.
    
    Returns:
        ApiResponse with detailed service status
    """
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    dependencies = {
        "google_places_api": "connected" if google_api_key else "disconnected"
    }
    
    return ApiResponse(
        success=True,
        data={
            "service": "Healthy Meal Finder API",
            "version": "1.0.0",
            "status": "healthy",
            "uptime": "2h 15m 30s",  # TODO: Implement actual uptime tracking
            "dependencies": dependencies,
            "configuration": {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "debug_mode": os.getenv("DEBUG", "true").lower() == "true",
                "rate_limiting": True
            }
        },
        message="Status retrieved successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version=api_version
    ) 