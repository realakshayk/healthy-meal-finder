import requests
from typing import Optional, List, Dict, Any

class HealthyMealFinderClient:
    """
    Python SDK for Healthy Meal Finder API.
    Usage:
        client = HealthyMealFinderClient(api_key="your_partner_key", base_url="http://localhost:8000/api/v1")
        meals = client.find_meals(lat=40.7128, lon=-74.0060, goal="muscle_gain")
    """
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def find_meals(self, lat: float, lon: float, goal: str, radius_miles: float = 5, max_results: Optional[int] = None, exclude_ingredients: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Find healthy meal recommendations by location and fitness goal.
        """
        payload = {
            "lat": lat,
            "lon": lon,
            "goal": goal,
            "radius_miles": radius_miles
        }
        if max_results:
            payload["max_results"] = max_results
        if exclude_ingredients:
            payload["exclude_ingredients"] = exclude_ingredients
        resp = requests.post(f"{self.base_url}/meals/find", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def estimate_nutrition(self, meal_description: str, serving_size: str = "1 serving") -> Dict[str, Any]:
        """
        Estimate nutrition for a meal description using AI.
        """
        payload = {
            "meal_description": meal_description,
            "serving_size": serving_size
        }
        resp = requests.post(f"{self.base_url}/nutrition/estimate", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_goals(self) -> Dict[str, Any]:
        """
        Get available fitness goals.
        """
        resp = requests.get(f"{self.base_url}/meals/goals", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def freeform_search(self, query: str, lat: float, lon: float) -> Dict[str, Any]:
        """
        Search for meals using a freeform natural language query.
        """
        payload = {
            "query": query,
            "lat": lat,
            "lon": lon
        }
        resp = requests.post(f"{self.base_url}/meals/freeform-search", json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        """
        resp = requests.get(f"{self.base_url}/health/", headers=self.headers)
        resp.raise_for_status()
        return resp.json() 