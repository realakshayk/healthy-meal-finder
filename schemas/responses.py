# schemas/responses.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, TypeVar, Union, Generic

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper for consistent response formatting.
    """
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    error: Optional[str] = Field(None, description="Error message if success is False")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    timestamp: str = Field(..., description="ISO timestamp of the response")
    api_version: str = Field(..., description="API version")
    error_code: Optional[str] = Field(None, description="Unique error code for programmatic handling", example="ERR_INVALID_GOAL")
    trace_id: Optional[str] = Field(None, description="Unique trace ID for debugging and support", example="abc123-def456")
    support_link: Optional[str] = Field(None, description="Optional link to support resources", example="https://support.healthymealfinder.com/errors/ERR_INVALID_GOAL")

class RestaurantLocation(BaseModel):
    """
    Geographic location information for a restaurant.
    """
    lat: float = Field(..., description="Restaurant latitude", example=40.7128)
    lng: float = Field(..., description="Restaurant longitude", example=-74.0060)

class Restaurant(BaseModel):
    """
    Restaurant information including location and ratings.
    """
    name: str = Field(..., description="Restaurant name", example="Sweetgreen - SoHo")
    place_id: str = Field(..., description="Google Places API place ID", example="ChIJN1t_tDeuEmsRUsoyG83frY4")
    address: str = Field(..., description="Restaurant address", example="123 Main St, New York, NY")
    rating: Optional[float] = Field(None, description="Restaurant rating (1-5)", example=4.5)
    user_ratings_total: Optional[int] = Field(None, description="Total number of ratings", example=1250)
    location: RestaurantLocation = Field(..., description="Restaurant coordinates")
    types: List[str] = Field(default_factory=list, description="Restaurant categories", example=["restaurant", "food", "establishment"])
    distance_miles: Optional[float] = Field(None, description="Distance from user location in miles", example=1.2)

class NutritionInfo(BaseModel):
    """
    Nutritional information for a meal.
    """
    calories: int = Field(..., ge=0, description="Calories per serving", example=485)
    protein: int = Field(..., ge=0, description="Protein in grams", example=34)
    carbs: int = Field(..., ge=0, description="Carbohydrates in grams", example=29)
    fat: int = Field(..., ge=0, description="Fat in grams", example=21)

class MealRecommendation(BaseModel):
    """
    A recommended meal with nutritional information and scoring.
    """
    restaurant: str = Field(..., description="Restaurant name", example="Sweetgreen - SoHo")
    dish: str = Field(..., description="Dish name", example="Chicken + Brussels Bowl")
    description: Optional[str] = Field(None, description="Dish description", example="Grilled chicken with roasted Brussels sprouts")
    nutrition: NutritionInfo = Field(..., description="Nutritional information")
    distance_miles: float = Field(..., ge=0, description="Distance from user location in miles", example=1.2)
    score: int = Field(..., ge=0, le=4, description="Match score based on fitness goal (0-4)", example=3)
    goal_match: str = Field(..., description="Fitness goal this meal matches", example="muscle_gain")
    restaurant_info: Optional[Restaurant] = Field(None, description="Detailed restaurant information")

class FindMealsResponse(BaseModel):
    """
    Response model for meal recommendations.
    
    Returns a list of meal recommendations sorted by relevance to the user's
    fitness goals and location preferences.
    """
    meals: List[MealRecommendation] = Field(..., description="List of recommended meals")
    total_found: int = Field(..., description="Total number of meals found", example=25)
    search_radius: float = Field(..., description="Search radius used in miles", example=5.0)
    goal: str = Field(..., description="Fitness goal used for recommendations", example="muscle_gain")
    
    class Config:
        json_schema_extra = {
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

class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    error: str = Field(..., description="Error message", example="Invalid fitness goal provided")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code", example=400)
    error_code: Optional[str] = Field(None, description="Unique error code for programmatic handling", example="ERR_INVALID_GOAL")
    trace_id: Optional[str] = Field(None, description="Unique trace ID for debugging and support", example="abc123-def456")
    support_link: Optional[str] = Field(None, description="Optional link to support resources", example="https://support.healthymealfinder.com/errors/ERR_INVALID_GOAL") 