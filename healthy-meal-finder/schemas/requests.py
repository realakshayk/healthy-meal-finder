# schemas/requests.py

from pydantic import BaseModel, Field, validator
from typing import Literal, Union, Optional, List

class FindMealsRequest(BaseModel):
    """
    Request model for finding healthy meals based on location and fitness goals.
    
    This endpoint helps users discover healthy meal options near their location
    that align with their specific fitness and nutrition goals.
    
    The goal field accepts natural language input and will automatically match
    to the appropriate fitness goal using fuzzy string matching.
    
    Examples of accepted goal inputs:
    - "muscle_gain", "musle gain", "lean bulk", "bulking"
    - "weight_loss", "lose weight", "fat loss", "cutting"
    - "keto", "ketogenic", "low carb", "keto diet"
    - "balanced", "healthy eating", "maintenance"
    """
    
    lat: float = Field(description="Latitude coordinate of the user's location", example=40.7128)
    lon: float = Field(description="Longitude coordinate of the user's location", example=-74.0060)
    goal: Union[str, List[str]] = Field(
        description="Fitness goal(s) (accepts a string or list of natural language goals, e.g. ['keto', 'muscle_gain'])",
        example=["keto", "muscle_gain"]
    )
    cuisine: Optional[str] = Field(
        default=None,
        description="Preferred cuisine type (e.g., 'japanese', 'italian', 'indian')",
        example="japanese"
    )
    flavor_profile: Optional[str] = Field(
        default=None,
        description="Preferred flavor profile (e.g., 'savory', 'spicy', 'umami')",
        example="savory"
    )
    radius_miles: float = Field(description="Search radius in miles (maximum 50 miles)", example=5.0)
    max_results: int = Field(default=5, description="Maximum number of meal recommendations to return", example=5)
    restaurant_limit: int = Field(default=5, description="Maximum number of restaurants to process and scrape", example=5)
    exclude_ingredients: Optional[List[str]] = Field(
        default=None,
        description="List of ingredients to exclude from meal results (e.g., ['peanuts', 'gluten'])",
        example=["peanuts", "gluten"]
    )
    
    @validator('goal')
    def validate_goal(cls, v):
        """
        Validate and normalize the goal input(s) using fuzzy matching.
        """
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Goal cannot be empty")
            return v.strip()
        elif isinstance(v, list):
            if not v:
                raise ValueError("Goal list cannot be empty")
            return [item.strip() for item in v if item.strip()]
        else:
            raise ValueError("Goal must be a string or list of strings")
    
    @validator('radius_miles')
    def validate_radius(cls, v):
        """
        Validate search radius is within reasonable limits.
        """
        if v < 0.5 or v > 10:
            raise ValueError("Search radius must be between 0.5 and 10 miles")
        return v
    
    @validator('max_results')
    def validate_max_results(cls, v):
        """
        Validate max results is within reasonable limits.
        """
        if v < 1 or v > 15:
            raise ValueError("Max results must be between 1 and 15")
        return v
    
    @validator('restaurant_limit')
    def validate_restaurant_limit(cls, v):
        """
        Validate restaurant limit is within reasonable limits.
        """
        if v < 1 or v > 20:
            raise ValueError("Restaurant limit must be between 1 and 20")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 40.7128,
                "lon": -74.0060,
                "goal": "musle gain",
                "cuisine": "japanese",
                "flavor_profile": "savory",
                "radius_miles": 1.24,
                "max_results": 5,
                "restaurant_limit": 5
            }
        }

class NutritionEstimationRequest(BaseModel):
    """
    Request model for nutrition estimation from meal descriptions.
    
    This endpoint uses AI to estimate nutritional content from natural
    language meal descriptions, providing realistic estimates for calories,
    protein, carbohydrates, and fat.
    """
    
    meal_description: str = Field(
        description="Natural language description of the meal",
        example="Grilled chicken breast with quinoa and roasted vegetables"
    )
    
    serving_size: str = Field(
        default="1 serving",
        description="Serving size description (e.g., '1 serving', '1 cup', '200g')",
        example="1 serving"
    )
    
    @validator('meal_description')
    def validate_meal_description(cls, v):
        """
        Validate that meal description is not empty.
        """
        if not v or not v.strip():
            raise ValueError("Meal description cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
                "serving_size": "1 serving"
            }
        } 

class FreeformMealSearchRequest(BaseModel):
    """
    Request model for freeform meal search queries.
    """
    query: str = Field(
        description="Freeform search query, e.g. 'show me low-carb lunch near me'",
        example="show me low-carb lunch near me"
    )
    lat: Optional[float] = Field(
        default=None,
        description="Latitude coordinate of the user's location (optional if using 'near me')",
        example=40.7128
    )
    lon: Optional[float] = Field(
        default=None,
        description="Longitude coordinate of the user's location (optional if using 'near me')",
        example=-74.0060
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "show me low-carb lunch near me",
                "lat": 40.7128,
                "lon": -74.0060
            }
        } 