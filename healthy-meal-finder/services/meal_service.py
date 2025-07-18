# services/meal_service.py

import logging
import httpx
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from fitness_goals import get_nutrition_rules
from menu_generator import generate_mock_menu
from meal_utils import get_scored_meals

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

class MealService:
    """
    Service class for meal-related operations.
    
    This service handles:
    - Restaurant discovery via Google Places API
    - Menu generation and nutritional analysis
    - Meal scoring based on fitness goals
    """
    
    def __init__(self):
        self.google_api_key = GOOGLE_API_KEY
        if not self.google_api_key:
            logger.warning("Google Maps API key not found. Restaurant discovery will be limited.")
    
    def get_restaurants_from_google(self, lat: float, lon: float, radius_miles: float) -> List[Dict[str, Any]]:
        """
        Get restaurants from Google Places API.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate  
            radius_miles: Search radius in miles
            
        Returns:
            List of restaurant information dictionaries
        """
        if not self.google_api_key:
            logger.warning("No Google API key available, using mock restaurants")
            return self._get_mock_restaurants(lat, lon, radius_miles)
        
        radius_meters = int(radius_miles * 1609.34)
        
        params = {
            "location": f"{lat},{lon}",
            "radius": radius_meters,
            "type": "restaurant",
            "keyword": "healthy",
            "key": self.google_api_key
        }
        
        try:
            response = httpx.get(GOOGLE_PLACES_URL, params=params, timeout=10.0)
            response.raise_for_status()
            
            places = response.json().get("results", [])
            restaurants = []
            
            for place in places:
                restaurants.append({
                    "name": place.get("name"),
                    "place_id": place.get("place_id"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total"),
                    "location": place.get("geometry", {}).get("location", {}),
                    "types": place.get("types", []),
                    "distance_miles": None  # Optional: calculate later
                })
            
            logger.info(f"Found {len(restaurants)} restaurants from Google Places API")
            return restaurants
            
        except httpx.RequestError as e:
            logger.error(f"Error calling Google Places API: {e}")
            return self._get_mock_restaurants(lat, lon, radius_miles)
        except Exception as e:
            logger.error(f"Unexpected error in Google Places API call: {e}")
            return self._get_mock_restaurants(lat, lon, radius_miles)
    
    def _get_mock_restaurants(self, lat: float, lon: float, radius_miles: float) -> List[Dict[str, Any]]:
        """
        Get mock restaurant data when Google API is unavailable.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            radius_miles: Search radius in miles
            
        Returns:
            List of mock restaurant information
        """
        mock_restaurants = [
            {
                "name": "Sweetgreen - SoHo",
                "place_id": "mock_place_1",
                "address": "123 Main St, New York, NY",
                "rating": 4.5,
                "user_ratings_total": 1250,
                "location": {"lat": lat + 0.01, "lng": lon + 0.01},
                "types": ["restaurant", "food", "establishment"],
                "distance_miles": 1.2
            },
            {
                "name": "Chipotle - Broadway", 
                "place_id": "mock_place_2",
                "address": "456 Broadway, New York, NY",
                "rating": 4.2,
                "user_ratings_total": 890,
                "location": {"lat": lat - 0.01, "lng": lon - 0.01},
                "types": ["restaurant", "food", "establishment"],
                "distance_miles": 2.5
            },
            {
                "name": "Dig - Park Ave",
                "place_id": "mock_place_3", 
                "address": "789 Park Ave, New York, NY",
                "rating": 4.3,
                "user_ratings_total": 567,
                "location": {"lat": lat + 0.02, "lng": lon - 0.02},
                "types": ["restaurant", "food", "establishment"],
                "distance_miles": 3.1
            }
        ]
        
        logger.info(f"Using {len(mock_restaurants)} mock restaurants")
        return mock_restaurants
    
    def find_meals(self, lat: float, lon: float, goal: str, radius_miles: float, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find meal recommendations based on location and fitness goal.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            goal: Fitness goal (muscle_gain, weight_loss, keto, balanced)
            radius_miles: Search radius in miles
            max_results: Maximum number of results to return
            
        Returns:
            List of meal recommendations with scoring
        """
        logger.info(f"Finding meals for goal: {goal} at location ({lat}, {lon}) within {radius_miles} miles")
        
        # Get restaurants
        restaurants = self.get_restaurants_from_google(lat, lon, radius_miles)
        logger.info(f"Found {len(restaurants)} restaurants")
        
        # Get nutrition rules for the goal
        rules = get_nutrition_rules(goal)
        logger.info(f"Using nutrition rules for {goal}: {rules}")
        
        all_scored_meals = []
        
        # Generate meals for each restaurant
        for restaurant in restaurants:
            name = restaurant["name"]
            menu_items = generate_mock_menu(name)
            scored_items = get_scored_meals(menu_items, rules)
            
            # Add restaurant info and goal match to each meal
            for item in scored_items:
                item["goal_match"] = goal
                item["restaurant_info"] = restaurant
            
            all_scored_meals.extend(scored_items)
        
        logger.info(f"Generated {len(all_scored_meals)} scored meals")
        
        # Sort by score and limit results
        all_scored_meals.sort(key=lambda x: x["score"], reverse=True)
        
        if max_results:
            all_scored_meals = all_scored_meals[:max_results]
        
        return all_scored_meals

# Global service instance
meal_service = MealService()

def find_meals(lat: float, lon: float, goal: str, radius_miles: float, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to find meals using the global service instance.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        goal: Fitness goal
        radius_miles: Search radius in miles
        max_results: Maximum number of results to return
        
    Returns:
        List of meal recommendations
    """
    return meal_service.find_meals(lat, lon, goal, radius_miles, max_results)


