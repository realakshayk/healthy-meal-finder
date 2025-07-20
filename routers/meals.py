# routers/meals.py

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from schemas.requests import FindMealsRequest
from schemas.responses import FindMealsResponse, ErrorResponse
from services.meal_service import find_meals

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/meals",
    tags=["meals"],
    responses={
        404: {"model": ErrorResponse, "description": "No meals found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

@router.post(
    "/find",
    response_model=FindMealsResponse,
    summary="Find Healthy Meals",
    description="""
    Find healthy meal recommendations based on location and fitness goals.
    
    This endpoint searches for restaurants near the provided coordinates and returns
    meal recommendations that align with the specified fitness goal. The service:
    
    - Searches for healthy restaurants within the specified radius
    - Analyzes menu items for nutritional content
    - Scores meals based on fitness goal requirements
    - Returns top recommendations sorted by relevance
    
    **Supported Fitness Goals:**
    - `muscle_gain`: High protein, moderate calories
    - `weight_loss`: Lower calories, moderate protein
    - `keto`: Low carbs, high fat
    - `balanced`: General healthy eating guidelines
    """,
    responses={
        200: {
            "description": "Successfully found meal recommendations",
            "content": {
                "application/json": {
                    "example": {
                        "meals": [
                            {
                                "restaurant": "Sweetgreen - SoHo",
                                "dish": "Chicken + Brussels Bowl",
                                "description": "Grilled chicken with roasted Brussels sprouts",
                                "nutrition": {
                                    "calories": 485,
                                    "protein": 34,
                                    "carbs": 29,
                                    "fat": 21
                                },
                                "distance_miles": 1.2,
                                "score": 3,
                                "goal_match": "muscle_gain",
                                "restaurant_info": {
                                    "name": "Sweetgreen - SoHo",
                                    "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                                    "address": "123 Main St, New York, NY",
                                    "rating": 4.5,
                                    "user_ratings_total": 1250,
                                    "location": {"lat": 40.7128, "lng": -74.0060},
                                    "types": ["restaurant", "food", "establishment"],
                                    "distance_miles": 1.2
                                }
                            }
                        ],
                        "total_found": 25,
                        "search_radius": 5.0,
                        "goal": "muscle_gain"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid fitness goal provided",
                        "detail": "Goal must be one of: muscle_gain, weight_loss, keto, balanced",
                        "status_code": 400
                    }
                }
            }
        },
        404: {
            "description": "No meals found in the specified area",
            "content": {
                "application/json": {
                    "example": {
                        "error": "No meals found",
                        "detail": "No restaurants found within 5 miles of the specified location",
                        "status_code": 404
                    }
                }
            }
        }
    }
)
async def find_meals_endpoint(request: FindMealsRequest):
    """
    Find healthy meal recommendations based on location and fitness goals.
    
    Args:
        request: FindMealsRequest containing location, goal, and search parameters
        
    Returns:
        FindMealsResponse with recommended meals and metadata
        
    Raises:
        HTTPException: If no meals are found or invalid parameters provided
    """
    try:
        logger.info(f"Finding meals for goal: {request.goal} at location ({request.lat}, {request.lon})")
        
        meals = find_meals(
            lat=request.lat,
            lon=request.lon,
            goal=request.goal,
            radius_miles=request.radius_miles
        )
        
        if not meals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No meals found within {request.radius_miles} miles of the specified location"
            )
        
        # Limit results if specified
        if request.max_results and len(meals) > request.max_results:
            meals = meals[:request.max_results]
        
        return FindMealsResponse(
            meals=meals,
            total_found=len(meals),
            search_radius=request.radius_miles,
            goal=request.goal
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding meals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing meal request"
        )

@router.get(
    "/goals",
    summary="Get Available Fitness Goals",
    description="""
    Get a list of all available fitness goals and their descriptions.
    
    This endpoint returns information about the supported fitness goals
    that can be used when searching for meal recommendations.
    """,
    responses={
        200: {
            "description": "Successfully retrieved fitness goals",
            "content": {
                "application/json": {
                    "example": {
                        "goals": [
                            {
                                "id": "muscle_gain",
                                "name": "Muscle Gain",
                                "description": "High protein, moderate calories for muscle building",
                                "nutrition_focus": ["high_protein", "moderate_calories"]
                            },
                            {
                                "id": "weight_loss",
                                "name": "Weight Loss",
                                "description": "Lower calories, moderate protein for weight loss",
                                "nutrition_focus": ["low_calories", "moderate_protein"]
                            },
                            {
                                "id": "keto",
                                "name": "Ketogenic Diet",
                                "description": "Low carbs, high fat for ketosis",
                                "nutrition_focus": ["low_carbs", "high_fat"]
                            },
                            {
                                "id": "balanced",
                                "name": "Balanced Diet",
                                "description": "General healthy eating guidelines",
                                "nutrition_focus": ["balanced_macros"]
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_fitness_goals():
    """
    Get available fitness goals and their descriptions.
    
    Returns:
        Dictionary containing available fitness goals with descriptions
    """
    goals = [
        {
            "id": "muscle_gain",
            "name": "Muscle Gain",
            "description": "High protein, moderate calories for muscle building",
            "nutrition_focus": ["high_protein", "moderate_calories"]
        },
        {
            "id": "weight_loss",
            "name": "Weight Loss", 
            "description": "Lower calories, moderate protein for weight loss",
            "nutrition_focus": ["low_calories", "moderate_protein"]
        },
        {
            "id": "keto",
            "name": "Ketogenic Diet",
            "description": "Low carbs, high fat for ketosis",
            "nutrition_focus": ["low_carbs", "high_fat"]
        },
        {
            "id": "balanced",
            "name": "Balanced Diet",
            "description": "General healthy eating guidelines", 
            "nutrition_focus": ["balanced_macros"]
        }
    ]
    
    return {"goals": goals} 