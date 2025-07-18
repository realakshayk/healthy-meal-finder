# core/error_handlers.py

from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class HealthyMealFinderException(HTTPException):
    """
    Base exception class for Healthy Meal Finder API with structured error information.
    """
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[str] = None,
        support_link: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.error_code = error_code
        self.support_link = support_link or f"https://support.healthymealfinder.com/errors/{error_code}"
        super().__init__(status_code=status_code, detail=detail or message, headers=headers)

# Specific error classes for different scenarios
class InvalidGoalException(HealthyMealFinderException):
    """Raised when an invalid fitness goal is provided."""
    def __init__(self, goal: str, suggestions: Optional[list] = None):
        suggestion_text = ""
        if suggestions:
            suggestion_text = f" Did you mean: {', '.join([f'{name} ({goal_id})' for goal_id, name, score in suggestions[:2]])}?"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ERR_INVALID_GOAL",
            message="Invalid fitness goal provided",
            detail=f"Could not understand fitness goal '{goal}'.{suggestion_text}",
            headers={"X-Error-Code": "ERR_INVALID_GOAL"}
        )

class NoMealsFoundException(HealthyMealFinderException):
    """Raised when no meals are found for the given criteria."""
    def __init__(self, radius_miles: float, lat: float, lon: float):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ERR_NO_MEALS_FOUND",
            message="No meals found",
            detail=f"No meals found within {radius_miles} miles of location ({lat}, {lon})",
            headers={"X-Error-Code": "ERR_NO_MEALS_FOUND"}
        )

class InvalidLocationException(HealthyMealFinderException):
    """Raised when invalid location coordinates are provided."""
    def __init__(self, lat: float, lon: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ERR_INVALID_LOCATION",
            message="Invalid location coordinates",
            detail=f"Coordinates ({lat}, {lon}) are outside valid range. Latitude must be between -90 and 90, longitude between -180 and 180.",
            headers={"X-Error-Code": "ERR_INVALID_LOCATION"}
        )

class InvalidRadiusException(HealthyMealFinderException):
    """Raised when an invalid search radius is provided."""
    def __init__(self, radius: float):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ERR_INVALID_RADIUS",
            message="Invalid search radius",
            detail=f"Search radius {radius} miles is invalid. Must be between 0.1 and 50 miles.",
            headers={"X-Error-Code": "ERR_INVALID_RADIUS"}
        )

class NutritionEstimationException(HealthyMealFinderException):
    """Raised when nutrition estimation fails."""
    def __init__(self, meal_description: str, reason: str = "Unknown error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="ERR_NUTRITION_ESTIMATION_FAILED",
            message="Nutrition estimation failed",
            detail=f"Failed to estimate nutrition for meal: '{meal_description}'. Reason: {reason}",
            headers={"X-Error-Code": "ERR_NUTRITION_ESTIMATION_FAILED"}
        )

class ExternalServiceException(HealthyMealFinderException):
    """Raised when external services (Google Maps, OpenAI) are unavailable."""
    def __init__(self, service: str, operation: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="ERR_EXTERNAL_SERVICE_UNAVAILABLE",
            message=f"{service} service unavailable",
            detail=f"Unable to {operation} due to {service} service being unavailable. Please try again later.",
            headers={"X-Error-Code": "ERR_EXTERNAL_SERVICE_UNAVAILABLE"}
        )

class RateLimitExceededException(HealthyMealFinderException):
    """Raised when rate limit is exceeded."""
    def __init__(self, partner_id: str, plan: str, used: int, limit: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="ERR_RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded",
            detail=f"Rate limit exceeded for partner '{partner_id}'. Plan: {plan}, Used: {used}, Limit: {limit}",
            headers={
                "X-Error-Code": "ERR_RATE_LIMIT_EXCEEDED",
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(max(0, limit - used)),
                "X-RateLimit-Reset": "60"  # Reset in 60 seconds
            }
        )

class InvalidAPIKeyException(HealthyMealFinderException):
    """Raised when an invalid API key is provided."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="ERR_INVALID_API_KEY",
            message="Invalid or missing API key",
            detail="Invalid or missing API key. Set X-API-Key header with a valid API key.",
            headers={
                "X-Error-Code": "ERR_INVALID_API_KEY",
                "WWW-Authenticate": "API-Key"
            }
        )

class ValidationException(HealthyMealFinderException):
    """Raised when request validation fails."""
    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="ERR_VALIDATION_FAILED",
            message="Request validation failed",
            detail=f"Invalid value '{value}' for field '{field}': {reason}",
            headers={"X-Error-Code": "ERR_VALIDATION_FAILED"}
        )

class DatabaseException(HealthyMealFinderException):
    """Raised when database operations fail."""
    def __init__(self, operation: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="ERR_DATABASE_ERROR",
            message="Database operation failed",
            detail=f"Failed to {operation}. Please try again later.",
            headers={"X-Error-Code": "ERR_DATABASE_ERROR"}
        )

class ConfigurationException(HealthyMealFinderException):
    """Raised when there's a configuration error."""
    def __init__(self, config_key: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="ERR_CONFIGURATION_ERROR",
            message="Configuration error",
            detail=f"Missing or invalid configuration for '{config_key}'",
            headers={"X-Error-Code": "ERR_CONFIGURATION_ERROR"}
        )

# Utility functions for common error scenarios
def handle_validation_error(field: str, value: Any, reason: str) -> None:
    """Handle validation errors with structured exception."""
    raise ValidationException(field, value, reason)

def handle_external_service_error(service: str, operation: str) -> None:
    """Handle external service errors with structured exception."""
    logger.error(f"{service} service error during {operation}")
    raise ExternalServiceException(service, operation)

def handle_database_error(operation: str) -> None:
    """Handle database errors with structured exception."""
    logger.error(f"Database error during {operation}")
    raise DatabaseException(operation)

def handle_configuration_error(config_key: str) -> None:
    """Handle configuration errors with structured exception."""
    logger.error(f"Configuration error for {config_key}")
    raise ConfigurationException(config_key)

# Error code mapping for consistent error handling
ERROR_CODES = {
    "invalid_goal": "ERR_INVALID_GOAL",
    "no_meals_found": "ERR_NO_MEALS_FOUND", 
    "invalid_location": "ERR_INVALID_LOCATION",
    "invalid_radius": "ERR_INVALID_RADIUS",
    "nutrition_estimation_failed": "ERR_NUTRITION_ESTIMATION_FAILED",
    "external_service_unavailable": "ERR_EXTERNAL_SERVICE_UNAVAILABLE",
    "rate_limit_exceeded": "ERR_RATE_LIMIT_EXCEEDED",
    "invalid_api_key": "ERR_INVALID_API_KEY",
    "validation_failed": "ERR_VALIDATION_FAILED",
    "database_error": "ERR_DATABASE_ERROR",
    "configuration_error": "ERR_CONFIGURATION_ERROR",
    "unknown_error": "ERR_UNKNOWN"
} 