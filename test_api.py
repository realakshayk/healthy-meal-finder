# test_api.py

import requests
import pytest
import json

BASE_URL = "http://localhost:8000/api/v1/meals"
HEADERS = {"x-api-key": "testkey123", "Content-Type": "application/json"}

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_post_meals_find():
    payload = {
        "lat": 40.7128,
        "lon": -74.0060,
        "goal": "muscle_gain",
        "radius_miles": 5
    }
    resp = requests.post(f"{BASE_URL}/find", json=payload, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data and data["success"] is True
    assert "data" in data
    assert "meals" in data["data"]

def test_post_meals_freeform_search():
    payload = {"query": "show me high protein lunch"}
    resp = requests.post(f"{BASE_URL}/freeform-search", json=payload, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data and data["success"] is True
    assert "data" in data
    assert "meals" in data["data"]

def test_get_meals_goals():
    resp = requests.get(f"{BASE_URL}/goals", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data and data["success"] is True
    assert "data" in data
    assert "goals" in data["data"]

def test_get_meals_nutrition_rules():
    goal = "muscle_gain"
    resp = requests.get(f"{BASE_URL}/nutrition-rules/{goal}", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data and data["success"] is True
    assert "data" in data
    assert "goal" in data["data"]
    assert data["data"]["goal"] == goal

def test_get_meals_match_goal():
    user_input = "musle gain"
    resp = requests.get(f"{BASE_URL}/match-goal/{user_input}", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data and data["success"] is True
    assert "data" in data
    assert "matched_goal" in data["data"]

def test_root():
    """Test the root endpoint."""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("Testing Healthy Meal Finder API")
    print("=" * 40)
    
    try:
        test_root()
        test_health_check()
        test_post_meals_find()
        test_post_meals_freeform_search()
        test_get_meals_goals()
        test_get_meals_nutrition_rules()
        test_get_meals_match_goal()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}") 