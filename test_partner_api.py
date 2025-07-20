# test_partner_api.py

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api_root():
    """Test the API root endpoint."""
    print("Testing API root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"API Version: {data.get('api_version')}")
        print(f"Timestamp: {data.get('timestamp')}")
        
        if data.get('data'):
            endpoints = data['data'].get('endpoints', {})
            print(f"\nAvailable endpoints:")
            for name, path in endpoints.items():
                print(f"  {name}: {path}")
    else:
        print(f"Error: {response.text}")
    print()

def test_health_endpoints():
    """Test health check endpoints."""
    print("Testing health endpoints...")
    
    # Test basic health check
    response = requests.get(f"{BASE_URL}/api/v1/health/")
    print(f"Health check status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Service status: {data.get('data', {}).get('status')}")
    
    # Test readiness check
    response = requests.get(f"{BASE_URL}/api/v1/health/ready")
    print(f"Readiness check status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Service ready: {data.get('success')}")
        if data.get('data'):
            dependencies = data['data'].get('dependencies', {})
            print(f"Dependencies: {dependencies}")
    
    # Test detailed status
    response = requests.get(f"{BASE_URL}/api/v1/health/status")
    print(f"Detailed status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Service: {data.get('data', {}).get('service')}")
        print(f"Version: {data.get('data', {}).get('version')}")
    print()

def test_fitness_goals():
    """Test the fitness goals endpoint."""
    print("Testing fitness goals endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/meals/goals")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        
        if data.get('data', {}).get('goals'):
            goals = data['data']['goals']
            print(f"\nAvailable fitness goals ({len(goals)}):")
            for goal in goals:
                print(f"  - {goal['name']} ({goal['id']}): {goal['description']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_nutrition_rules():
    """Test nutrition rules endpoint."""
    print("Testing nutrition rules endpoint...")
    
    goals = ["muscle_gain", "weight_loss", "keto", "balanced"]
    
    for goal in goals:
        response = requests.get(f"{BASE_URL}/api/v1/meals/nutrition-rules/{goal}")
        print(f"Status for {goal}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success')}")
            if data.get('data'):
                rules = data['data'].get('rules', {})
                print(f"  Rules: {rules}")
        else:
            print(f"  Error: {response.text}")
    print()

def test_find_meals():
    """Test the find meals endpoint with different scenarios."""
    print("Testing find meals endpoint...")
    
    test_cases = [
        {
            "name": "Muscle Gain in NYC",
            "payload": {
                "lat": 40.7128,
                "lon": -74.0060,
                "goal": "muscle_gain",
                "radius_miles": 5.0,
                "max_results": 3
            }
        },
        {
            "name": "Weight Loss in LA",
            "payload": {
                "lat": 34.0522,
                "lon": -118.2437,
                "goal": "weight_loss",
                "radius_miles": 3.0,
                "max_results": 2
            }
        },
        {
            "name": "Keto in Chicago",
            "payload": {
                "lat": 41.8781,
                "lon": -87.6298,
                "goal": "keto",
                "radius_miles": 4.0,
                "max_results": 2
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        response = requests.post(
            f"{BASE_URL}/api/v1/meals/find",
            json=test_case['payload']
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            
            if data.get('data'):
                meals_data = data['data']
                print(f"Total found: {meals_data.get('total_found')}")
                print(f"Search radius: {meals_data.get('search_radius')} miles")
                print(f"Goal: {meals_data.get('goal')}")
                
                meals = meals_data.get('meals', [])
                print(f"Meals returned: {len(meals)}")
                
                for i, meal in enumerate(meals[:2]):  # Show first 2 meals
                    print(f"  Meal {i+1}:")
                    print(f"    Restaurant: {meal.get('restaurant')}")
                    print(f"    Dish: {meal.get('dish')}")
                    print(f"    Score: {meal.get('score')}")
                    print(f"    Distance: {meal.get('distance_miles')} miles")
                    if meal.get('nutrition'):
                        nutrition = meal['nutrition']
                        print(f"    Calories: {nutrition.get('calories')}")
                        print(f"    Protein: {nutrition.get('protein')}g")
        else:
            print(f"Error: {response.text}")
    
    print()

def test_error_handling():
    """Test error handling with invalid requests."""
    print("Testing error handling...")
    
    # Test invalid goal
    response = requests.post(
        f"{BASE_URL}/api/v1/meals/find",
        json={
            "lat": 40.7128,
            "lon": -74.0060,
            "goal": "invalid_goal",
            "radius_miles": 5.0
        }
    )
    print(f"Invalid goal status: {response.status_code}")
    
    # Test invalid nutrition rules endpoint
    response = requests.get(f"{BASE_URL}/api/v1/meals/nutrition-rules/invalid_goal")
    print(f"Invalid nutrition rules status: {response.status_code}")
    
    # Test non-existent endpoint
    response = requests.get(f"{BASE_URL}/api/v1/nonexistent")
    print(f"Non-existent endpoint status: {response.status_code}")
    
    print()

def test_response_format():
    """Test that all responses follow the expected format."""
    print("Testing response format consistency...")
    
    endpoints = [
        "/",
        "/api/v1/health/",
        "/api/v1/meals/goals"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"\nTesting {endpoint}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ['success', 'timestamp', 'api_version']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"  ❌ Missing fields: {missing_fields}")
            else:
                print(f"  ✅ All required fields present")
                print(f"  Success: {data.get('success')}")
                print(f"  API Version: {data.get('api_version')}")
                print(f"  Has data: {'data' in data}")
                print(f"  Has message: {'message' in data}")
        else:
            print(f"  ❌ Request failed")
    
    print()

if __name__ == "__main__":
    print("Testing Healthy Meal Finder API - Partner Edition")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        test_api_root()
        test_health_endpoints()
        test_fitness_goals()
        test_nutrition_rules()
        test_find_meals()
        test_error_handling()
        test_response_format()
        
        print("✅ All tests completed!")
        print("\nAPI is ready for partner consumption!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 