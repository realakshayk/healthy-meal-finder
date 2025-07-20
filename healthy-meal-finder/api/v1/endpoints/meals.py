# api/v1/endpoints/meals.py

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
import logging
from datetime import datetime

from schemas.requests import FindMealsRequest
from schemas.responses import FindMealsResponse, ErrorResponse, ApiResponse
from services.meal_service import find_meals
from core.dependencies import get_api_version
from core.goal_matcher import goal_matcher
from utils.freeform_query_parser import parse_freeform_query
from schemas.requests import FreeformMealSearchRequest
from core.analytics import log_meal_returned, log_goal_searched, get_all_stats
from core.error_handlers import (
    InvalidGoalException, NoMealsFoundException, InvalidLocationException,
    InvalidRadiusException, ExternalServiceException, ValidationException
)

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
    response_model=ApiResponse[FindMealsResponse],
    summary="Find Healthy Meals",
    description="""
    Find healthy meal recommendations based on location and fitness goals.
    
    This endpoint searches for restaurants near the provided coordinates and returns
    meal recommendations that align with the specified fitness goal. The service:
    
    - Searches for healthy restaurants within the specified radius
    - Scrapes restaurant websites for live menu data
    - Uses AI to parse and analyze menu items
    - Scores meals based on fitness goal requirements
    - Returns top recommendations sorted by relevance
    
    **Customizable Parameters:**
    - `radius_miles`: Search radius (0.5-10 miles)
    - `restaurant_limit`: Number of restaurants to process (1-20)
    - `max_results`: Number of meals to return (1-15)
    - `cuisine`: Preferred cuisine type (optional)
    - `flavor_profile`: Preferred flavor profile (optional)
    
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
                        "success": True,
                        "data": {
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
                        },
                        "message": "Meals found successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Invalid fitness goal provided",
                        "detail": "Goal must be one of: muscle_gain, weight_loss, keto, balanced",
                        "status_code": 400,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        },
        404: {
            "description": "No meals found in the specified area",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "No meals found",
                        "detail": "No restaurants found within 5 miles of the specified location",
                        "status_code": 404,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def find_meals_endpoint(
    request: FindMealsRequest,
    api_version: str = Depends(get_api_version)
):
    """
    Find healthy meal recommendations based on location and fitness goals.
    
    Args:
        request: FindMealsRequest containing location, goal, and search parameters
        api_version: API version from dependency injection
        
    Returns:
        ApiResponse with meal recommendations and metadata
        
    Raises:
        HTTPException: If no meals are found or invalid parameters provided
    """
    try:
        logger.info(f"Finding meals for goal: {request.goal} at location ({request.lat}, {request.lon})")
        # Support multiple goals
        goals = request.goal if isinstance(request.goal, list) else [request.goal]
        matched_goals = []
        confidences = []
        for g in goals:
            mg, conf = goal_matcher.match_goal(g)
            if mg:
                matched_goals.append(mg)
                confidences.append(conf)
        if not matched_goals:
            suggestions = []
            for g in goals:
                suggestions.extend(goal_matcher.get_suggestions(g))
            raise InvalidGoalException(str(request.goal), suggestions)
        # Log analytics for all searched goals
        for mg in matched_goals:
            log_goal_searched(mg)
        # Find meals for any of the matched goals (union)
        all_meals = []
        for mg in matched_goals:
            meals = await find_meals(
                lat=request.lat,
                lon=request.lon,
                goal=mg,
                radius_miles=request.radius_miles,
                max_results=request.max_results,
                restaurant_limit=request.restaurant_limit,
                cuisine=request.cuisine,
                flavor_profile=request.flavor_profile
            )
            all_meals.extend(meals)
        # Remove duplicates by dish name
        seen = set()
        unique_meals = []
        for meal in all_meals:
            dish = getattr(meal, 'dish', None) or (meal.get('dish') if isinstance(meal, dict) else None)
            if dish and dish not in seen:
                unique_meals.append(meal)
                seen.add(dish)
        # Exclude meals with any of the specified ingredients
        if request.exclude_ingredients:
            exclude_set = set(i.lower() for i in request.exclude_ingredients)
            def contains_excluded(meal):
                desc = (meal.get('description') or '').lower() if isinstance(meal, dict) else (getattr(meal, 'description', '') or '').lower()
                return any(ingredient in desc for ingredient in exclude_set)
            unique_meals = [meal for meal in unique_meals if not contains_excluded(meal)]
        # Log analytics for returned meals
        for meal in unique_meals:
            dish = getattr(meal, 'dish', None) or (meal.get('dish') if isinstance(meal, dict) else None)
            if dish:
                log_meal_returned(dish, dish)
        if not unique_meals:
            raise NoMealsFoundException(request.radius_miles, request.lat, request.lon)
        response_data = FindMealsResponse(
            meals=unique_meals,
            total_found=len(unique_meals),
            search_radius=request.radius_miles,
            goal=matched_goals[0] if matched_goals else "balanced"
        )
        message = f"Meals found successfully for goals: {matched_goals}"
        return ApiResponse(
            success=True,
            data=response_data,
            message=message,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version,
            error=None,
            detail=None,
            status_code=None,
            error_code=None,
            trace_id=None,
            support_link=None
        )
        
    except (HTTPException, InvalidGoalException, NoMealsFoundException):
        raise
    except Exception as e:
        logger.error(f"Error finding meals: {str(e)}")
        raise ExternalServiceException("Meal Service", "finding meals")

@router.post(
    "/freeform-search",
    response_model=ApiResponse,
    summary="Freeform Meal Search",
    description="""
    Search for meals using a freeform natural language query, e.g. 'show me low-carb lunch near me'.
    The query is parsed using keyword matching and basic NLP to extract meal type, dietary preference, calorie limits, and location intent.
    """,
)
async def freeform_meal_search(
    request: FreeformMealSearchRequest,
    api_version: str = Depends(get_api_version)
):
    """
    Freeform meal search endpoint.
    """
    # Parse the freeform query
    parsed = parse_freeform_query(request.query)

    # Map parsed filters to internal search logic
    # For demo: use FindMealsRequest and call existing meal search logic
    # (In production, you may want to further enhance this mapping)
    goal = parsed["dietary_preference"] or "balanced"
    # Use meal_type as a filter if your meal data supports it
    # Use calorie_limit as a filter if your meal data supports it
    lat = request.lat
    lon = request.lon
    if parsed["location"] == "near_me" and (not lat or not lon):
        # In a real app, you might use IP geolocation or prompt for location
        return ApiResponse(
            success=False,
            data=None,
            message="Please provide your latitude and longitude.",
            error="Location required for 'near me' searches.",
            detail="Location coordinates are required for 'near me' searches",
            status_code=400,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version,
            error_code="ERR_LOCATION_REQUIRED",
            trace_id=None,
            support_link="https://support.healthymealfinder.com/errors/ERR_LOCATION_REQUIRED"
        )
    # Use existing meal search logic (mocked here)
    # You would call your meal_service.find_meals() with the mapped filters
    # For now, just return the parsed filters for demonstration
    # Log analytics for searched goal
    if goal:
        log_goal_searched(goal)
    # If you return meals, also log_meal_returned for each
    return ApiResponse(
        success=True,
        data={
            "parsed_filters": parsed,
            "lat": lat,
            "lon": lon
        },
        message="Freeform query parsed successfully.",
        error=None,
        detail=None,
        status_code=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version=api_version,
        error_code=None,
        trace_id=None,
        support_link=None
    )

@router.get(
    "/goals",
    response_model=ApiResponse,
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
                        "success": True,
                        "data": {
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
                        },
                        "message": "Fitness goals retrieved successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def get_fitness_goals(api_version: str = Depends(get_api_version)):
    """
    Get available fitness goals and their descriptions.
    
    Returns:
        ApiResponse containing available fitness goals with descriptions and synonyms
    """
    all_goals = goal_matcher.get_all_goals()
    goals = []
    
    for goal_id, goal_info in all_goals.items():
        goals.append({
            "id": goal_id,
            "name": goal_info["name"],
            "description": goal_info["description"],
            "synonyms": goal_info["synonyms"][:10],  # Show first 10 synonyms
            "total_synonyms": len(goal_info["synonyms"])
        })
    
    return ApiResponse(
        success=True,
        data={"goals": goals},
        message="Fitness goals retrieved successfully",
        error=None,
        detail=None,
        status_code=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version=api_version,
        error_code=None,
        trace_id=None,
        support_link=None
    )

@router.get(
    "/nutrition-rules/{goal}",
    response_model=ApiResponse,
    summary="Get Nutrition Rules for Goal",
    description="""
    Get detailed nutrition rules and requirements for a specific fitness goal.
    
    This endpoint returns the nutritional criteria used to score meals
    for the specified fitness goal.
    """,
    responses={
        200: {
            "description": "Successfully retrieved nutrition rules",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "goal": "muscle_gain",
                            "rules": {
                                "min_protein": 25,
                                "max_calories": 800,
                                "max_carbs": 60
                            },
                            "description": "High protein, moderate calories for muscle building"
                        },
                        "message": "Nutrition rules retrieved successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        },
        400: {
            "description": "Invalid fitness goal",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "Invalid fitness goal",
                        "detail": "Goal must be one of: muscle_gain, weight_loss, keto, balanced",
                        "status_code": 400,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def get_nutrition_rules(
    goal: str,
    api_version: str = Depends(get_api_version)
):
    """
    Get nutrition rules for a specific fitness goal.
    
    Args:
        goal: Fitness goal identifier
        api_version: API version from dependency injection
        
    Returns:
        ApiResponse with nutrition rules for the goal
    """
    from fitness_goals import get_nutrition_rules
    
    valid_goals = {"muscle_gain", "weight_loss", "keto", "balanced"}
    
    if goal not in valid_goals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid goal: '{goal}'. Must be one of {', '.join(valid_goals)}."
        )
    
    rules = get_nutrition_rules(goal)
    
    goal_descriptions = {
        "muscle_gain": "High protein, moderate calories for muscle building",
        "weight_loss": "Lower calories, moderate protein for weight loss",
        "keto": "Low carbs, high fat for ketosis",
        "balanced": "General healthy eating guidelines"
    }
    
    return ApiResponse(
        success=True,
        data={
            "goal": goal,
            "rules": rules,
            "description": goal_descriptions.get(goal, "")
        },
        message="Nutrition rules retrieved successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
        api_version=api_version
    )

@router.get(
    "/match-goal/{user_input}",
    response_model=ApiResponse,
    summary="Test Goal Matching",
    description="""
    Test fuzzy matching for a user input string.
    
    This endpoint helps test and understand how natural language input
    gets matched to fitness goals using fuzzy string matching.
    """,
    responses={
        200: {
            "description": "Successfully matched goal",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "user_input": "musle gain",
                            "matched_goal": "muscle_gain",
                            "confidence": 95,
                            "goal_name": "Muscle Gain",
                            "suggestions": [
                                {"goal_id": "weight_loss", "name": "Weight Loss", "score": 45},
                                {"goal_id": "keto", "name": "Ketogenic Diet", "score": 30}
                            ]
                        },
                        "message": "Goal matched successfully",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        },
        400: {
            "description": "No match found",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": "No match found",
                        "detail": "Could not match 'invalid goal' to any fitness goal",
                        "status_code": 400,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "api_version": "v1"
                    }
                }
            }
        }
    }
)
async def test_goal_matching(
    user_input: str,
    api_version: str = Depends(get_api_version)
):
    """
    Test fuzzy matching for a user input string.
    
    Args:
        user_input: The user input to test
        api_version: API version from dependency injection
        
    Returns:
        ApiResponse with matching results and suggestions
    """
    matched_goal, confidence = goal_matcher.match_goal(user_input)
    suggestions = goal_matcher.get_suggestions(user_input, max_suggestions=3)
    
    if matched_goal:
        goal_info = goal_matcher.get_goal_info(matched_goal)
        goal_name = goal_info["name"] if goal_info else matched_goal
        
        return ApiResponse(
            success=True,
            data={
                "user_input": user_input,
                "matched_goal": matched_goal,
                "confidence": confidence,
                "goal_name": goal_name,
                "suggestions": [
                    {"goal_id": goal_id, "name": name, "score": score}
                    for goal_id, name, score in suggestions
                ]
            },
            message="Goal matched successfully",
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version
        )
    else:
        return ApiResponse(
            success=False,
            error="No match found",
            detail=f"Could not match '{user_input}' to any fitness goal",
            status_code=400,
            timestamp=datetime.utcnow().isoformat() + "Z",
            api_version=api_version
        ) 

@router.get(
    "/analytics",
    response_model=ApiResponse,
    summary="View meal and goal analytics (debug)",
    description="Returns top meals and goals searched (in-memory, resets on restart).",
)
async def get_analytics(api_version: str = Depends(get_api_version)):
    stats = get_all_stats()
    return ApiResponse(
        success=True,
        data=stats,
        message="Analytics stats returned.",
        api_version=api_version
    ) 