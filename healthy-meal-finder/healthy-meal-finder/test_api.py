# test_api.py

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/v1/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_fitness_goals():
    """Test the fitness goals endpoint."""
    print("Testing fitness goals...")
    response = requests.get(f"{BASE_URL}/api/v1/meals/goals")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_find_meals():
    """Test the find meals endpoint."""
    print("Testing find meals...")
    
    payload = {
        "lat": 40.7128,
        "lon": -74.0060,
        "goal": "muscle_gain",
        "radius_miles": 5.0,
        "max_results": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/meals/find", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_found']} meals")
        print(f"Search radius: {data['search_radius']} miles")
        print(f"Goal: {data['goal']}")
        
        if data['meals']:
            print("\nTop meal recommendation:")
            meal = data['meals'][0]
            print(f"  Restaurant: {meal['restaurant']}")
            print(f"  Dish: {meal['dish']}")
            print(f"  Score: {meal['score']}")
            print(f"  Distance: {meal['distance_miles']} miles")
    else:
        print(f"Error: {response.text}")
    print()

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
        test_fitness_goals()
        test_find_meals()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}") 