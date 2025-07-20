# services/meal_service.py

import logging
import httpx
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import shelve
import time

from fitness_goals import get_nutrition_rules
from menu_generator import generate_mock_menu
from meal_utils import get_scored_meals
from mock_meals import mock_meals

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

CACHE_FILE = "google_places_cache.db"
CACHE_TTL = 60 * 60 * 24  # 24 hours

class MealService:
    """
    Service class for meal-related operations.
    
    This service handles:
    - Restaurant discovery via Google Places API (with local caching)
    - Menu generation and nutritional analysis
    - Meal scoring based on fitness goals
    """
    
    def __init__(self):
        self.google_api_key = GOOGLE_API_KEY
        if not self.google_api_key:
            logger.warning("Google Maps API key not found. Restaurant discovery will be limited.")
    
    def get_restaurants_from_google(self, lat: float, lon: float, radius_miles: float, keyword: str = "healthy") -> List[Dict[str, Any]]:
        """
        Get restaurants from Google Places API, with local file-based caching.
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate  
            radius_miles: Search radius in miles
            keyword: Keyword for filtering restaurants (default: "healthy")
        Returns:
            List of restaurant information dictionaries
        """
        if not self.google_api_key:
            logger.warning("No Google API key available, using mock restaurants")
            return self._get_restaurants_from_mock_meals()
        
        radius_meters = int(radius_miles * 1609.34)
        cache_key = f"{lat:.4f},{lon:.4f}:{radius_miles:.2f}:{keyword}"
        now = time.time()
        # Try cache first
        with shelve.open(CACHE_FILE) as cache:
            if cache_key in cache:
                cached = cache[cache_key]
                if now - cached["timestamp"] < CACHE_TTL:
                    logger.info(f"Returning cached Google Places results for {cache_key}")
                    return cached["data"]
                else:
                    del cache[cache_key]
        params = {
            "location": f"{lat},{lon}",
            "radius": radius_meters,
            "type": "restaurant",
            "keyword": keyword,
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
                    "distance_miles": None
                })
            if not restaurants:
                logger.warning(f"Google Places API returned no results for {lat},{lon} (radius {radius_miles} mi). Falling back to mock meals.")
                return self._get_restaurants_from_mock_meals()
            logger.info(f"Found {len(restaurants)} restaurants from Google Places API")
            # Save to cache
            with shelve.open(CACHE_FILE) as cache:
                cache[cache_key] = {"timestamp": now, "data": restaurants}
            return restaurants
        except httpx.RequestError as e:
            logger.error(f"Error calling Google Places API: {e}")
            return self._get_restaurants_from_mock_meals()
        except Exception as e:
            logger.error(f"Unexpected error in Google Places API call: {e}")
            return self._get_restaurants_from_mock_meals()

    def _get_restaurants_from_mock_meals(self) -> List[Dict[str, Any]]:
        """
        Return a list of restaurant info dicts based on mock_meals for fallback.
        """
        # Extract unique restaurants from mock_meals
        seen = set()
        restaurants = []
        for meal in mock_meals:
            name = meal["restaurant"]
            if name not in seen:
                seen.add(name)
                restaurants.append({
                    "name": name,
                    "place_id": f"mock_{name.lower().replace(' ', '_')}",
                    "address": "Unknown address (mock)",
                    "rating": None,
                    "user_ratings_total": None,
                    "location": {},
                    "types": ["restaurant", "mock"],
                    "distance_miles": meal.get("distance_miles")
                })
        logger.info(f"Using {len(restaurants)} mock restaurants from mock_meals fallback.")
        return restaurants
    
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
                # Transform flat nutrition fields to nested structure
                nutrition = {
                    "calories": item.get("calories", 0),
                    "protein": item.get("protein", 0),
                    "carbs": item.get("carbs", 0),
                    "fat": item.get("fat", 0)
                }
                
                # Create properly structured meal
                structured_meal = {
                    "restaurant": item["restaurant"],
                    "dish": item["dish"],
                    "description": item.get("description"),
                    "nutrition": nutrition,
                    "distance_miles": item.get("distance_miles", 0.0),
                    "score": item["score"],
                    "goal_match": goal,
                    "restaurant_info": {
                        "name": restaurant["name"],
                        "place_id": restaurant["place_id"],
                        "address": restaurant["address"],
                        "rating": restaurant["rating"],
                        "user_ratings_total": restaurant["user_ratings_total"],
                        "location": {
                            "lat": restaurant["location"].get("lat", 0.0) if restaurant["location"] else 0.0,
                            "lng": restaurant["location"].get("lng", 0.0) if restaurant["location"] else 0.0
                        },
                        "types": restaurant["types"],
                        "distance_miles": restaurant.get("distance_miles")
                    }
                }
                
                all_scored_meals.append(structured_meal)
        
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


