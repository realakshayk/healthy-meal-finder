# api/v1/endpoints/nutrition.py

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
import logging
from datetime import datetime
import json

from schemas.requests import NutritionEstimationRequest
from schemas.responses import ApiResponse, ErrorResponse
from utils.nutrition_estimator import nutrition_estimator
from core.dependencies import get_api_version
from core.error_handlers import (
    NutritionEstimationException, ValidationException, ExternalServiceException
)

logger = logging.getLogger(__name__)

# Add a dedicated logger for nutrition estimation logs
nutrition_logger = logging.getLogger("nutrition_logger")
if not nutrition_logger.handlers:
    handler = logging.FileHandler("nutrition_estimations.log")
    handler.setFormatter(logging.Formatter('%(message)s'))
    nutrition_logger.addHandler(handler)
    nutrition_logger.setLevel(logging.INFO)

router = APIRouter(
    prefix="/nutrition",
    tags=["nutrition"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

@router.post(
    "/estimate",
    response_model=ApiResponse,
    summary="Estimate Nutrition from Meal Description",
    description="""
    Estimate nutritional content from a meal description using AI.
    
    This endpoint uses OpenAI to analyze meal descriptions and provide
    realistic estimates for calories, protein, carbohydrates, and fat.
    The estimation considers typical portion sizes, cooking methods,
    and ingredient combinations.
    
    **Features:**
    - AI-powered nutrition estimation
    - Fallback keyword-based estimation when OpenAI unavailable
    - Validation of nutrition estimates
    - Support for various meal descriptions and serving sizes
    """,
    responses={
        200: {
            "description": "Successfully estimated nutrition",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
                            "serving_size": "1 serving",
                            "nutrition": {
                                "calories": 485,
                                "protein": 34,
                                "carbs": 29,
                                "fat": 21
                            },
                            "confidence_score": 95,
                            "validation": {
                                "is_valid": True,
                                "message": "Valid nutrition estimate"
                            },
                            "estimation_method": "openai"
                        },
                        "message": "Nutrition estimated successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        },
        400: {
            "description": "Invalid meal description",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Invalid meal description",
                        "detail": "Meal description cannot be empty",
                        "status_code": 400,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def estimate_nutrition(
    request: NutritionEstimationRequest,
    api_version: str = Depends(get_api_version)
):
    """
    Estimate nutrition from a meal description.
    
    Args:
        request: NutritionEstimationRequest with meal description and serving size
        api_version: API version from dependency injection
        
    Returns:
        ApiResponse with estimated nutrition information
    """
    try:
        logger.info(f"Estimating nutrition for: '{request.meal_description}'")
        
        # Estimate nutrition
        nutrition = nutrition_estimator.estimate_nutrition(
            request.meal_description,
            request.serving_size
        )
        
        # Validate the estimate
        is_valid, validation_message = nutrition_estimator.validate_nutrition_estimate(nutrition)
        
        # Determine estimation method
        estimation_method = "openai" if nutrition_estimator.client else "fallback"
        
        response_data = {
            "meal_description": request.meal_description,
            "serving_size": request.serving_size,
            "nutrition": nutrition,
            "confidence_score": nutrition.get("confidence_score", 70),
            "validation": {
                "is_valid": is_valid,
                "message": validation_message
            },
            "estimation_method": estimation_method
        }
        if nutrition.get("fallback_used"):
            response_data["fallback_used"] = True
            response_data["warning_message"] = nutrition.get("warning_message")
        
        # Add warning if using fallback method
        message = "Nutrition estimated successfully"
        if estimation_method == "fallback":
            message = "Nutrition estimated successfully (using fallback method - OpenAI not available)"
        
        # --- LOGGING ---
        nutrition_logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input": {
                "meal_description": request.meal_description,
                "serving_size": request.serving_size
            },
            "output": {
                "nutrition": nutrition,
                "confidence_score": nutrition.get("confidence_score", 70),
                "estimation_method": estimation_method,
                "validation": {
                    "is_valid": is_valid,
                    "message": validation_message
                },
                "fallback_used": nutrition.get("fallback_used", False),
                "warning_message": nutrition.get("warning_message")
            }
        }))
        # --- END LOGGING ---
        
        return ApiResponse(
            success=True,
            data=response_data,
            message=message,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version
        )
        
    except Exception as e:
        logger.error(f"Error estimating nutrition: {str(e)}")
        raise NutritionEstimationException(request.meal_description, str(e))

@router.post(
    "/estimate-batch",
    response_model=ApiResponse,
    summary="Estimate Nutrition for Multiple Meals",
    description="""
    Estimate nutritional content for multiple meal descriptions in batch.
    
    This endpoint processes multiple meal descriptions and provides
    nutrition estimates for each one. Useful for bulk processing
    of menu items or meal plans.
    """,
    responses={
        200: {
            "description": "Successfully estimated nutrition for all meals",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "meals": [
                                {
                                    "meal_description": "Grilled chicken breast with quinoa",
                                    "serving_size": "1 serving",
                                    "nutrition": {
                                        "calories": 485,
                                        "protein": 34,
                                        "carbs": 29,
                                        "fat": 21
                                    },
                                    "confidence_score": 95
                                },
                                {
                                    "meal_description": "Caesar salad with grilled salmon",
                                    "serving_size": "1 serving",
                                    "nutrition": {
                                        "calories": 320,
                                        "protein": 28,
                                        "carbs": 15,
                                        "fat": 18
                                    },
                                    "confidence_score": 95
                                }
                            ],
                            "estimation_method": "openai",
                            "total_meals": 2
                        },
                        "message": "Batch nutrition estimation completed",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def estimate_nutrition_batch(
    request: List[NutritionEstimationRequest],
    api_version: str = Depends(get_api_version)
):
    """
    Estimate nutrition for multiple meal descriptions.
    
    Args:
        request: List of NutritionEstimationRequest objects
        api_version: API version from dependency injection
        
    Returns:
        ApiResponse with nutrition estimates for all meals
    """
    try:
        if not request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one meal description is required"
            )
        
        logger.info(f"Estimating nutrition for {len(request)} meals")
        
        # Extract meal descriptions
        meal_descriptions = [req.meal_description for req in request]
        
        # Estimate nutrition for all meals
        nutrition_results = nutrition_estimator.estimate_nutrition_batch(meal_descriptions)
        
        # Format results
        meals_data = []
        for i, nutrition in enumerate(nutrition_results):
            meals_data.append({
                "meal_description": meal_descriptions[i],
                "serving_size": request[i].serving_size,
                "nutrition": nutrition,
                "confidence_score": nutrition.get("confidence_score", 70)
            })
        
        # Determine estimation method
        estimation_method = "openai" if nutrition_estimator.client else "fallback"
        
        response_data = {
            "meals": meals_data,
            "estimation_method": estimation_method,
            "total_meals": len(meals_data)
        }
        
        message = f"Batch nutrition estimation completed for {len(meals_data)} meals"
        if estimation_method == "fallback":
            message += " (using fallback method - OpenAI not available)"
        
        return ApiResponse(
            success=True,
            data=response_data,
            message=message,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch nutrition estimation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in batch nutrition estimation"
        )

@router.get(
    "/validate/{calories}/{protein}/{carbs}/{fat}",
    response_model=ApiResponse,
    summary="Validate Nutrition Estimate",
    description="""
    Validate a nutrition estimate for reasonableness.
    
    This endpoint checks if the provided nutrition values are within
    reasonable ranges and if the calories match the macronutrient breakdown.
    """,
    responses={
        200: {
            "description": "Nutrition validation completed",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "nutrition": {
                                "calories": 485,
                                "protein": 34,
                                "carbs": 29,
                                "fat": 21
                            },
                            "validation": {
                                "is_valid": True,
                                "message": "Valid nutrition estimate"
                            },
                            "calculated_calories": 485
                        },
                        "message": "Nutrition validation completed",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def validate_nutrition(
    calories: int,
    protein: int,
    carbs: int,
    fat: int,
    api_version: str = Depends(get_api_version)
):
    """
    Validate a nutrition estimate.
    
    Args:
        calories: Estimated calories
        protein: Protein in grams
        carbs: Carbohydrates in grams
        fat: Fat in grams
        api_version: API version from dependency injection
        
    Returns:
        ApiResponse with validation results
    """
    try:
        nutrition = {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }
        
        # Validate the nutrition estimate
        is_valid, validation_message = nutrition_estimator.validate_nutrition_estimate(nutrition)
        
        # Calculate expected calories
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        
        response_data = {
            "nutrition": nutrition,
            "validation": {
                "is_valid": is_valid,
                "message": validation_message
            },
            "calculated_calories": calculated_calories
        }
        
        return ApiResponse(
            success=True,
            data=response_data,
            message="Nutrition validation completed",
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version
        )
        
    except Exception as e:
        logger.error(f"Error validating nutrition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating nutrition"
        ) 