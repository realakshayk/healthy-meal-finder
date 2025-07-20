#!/usr/bin/env python3
"""
Comprehensive API testing script for Good Eats MVP
Tests all endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
HEADERS = {"x-api-key": "testkey123", "Content-Type": "application/json"}

def test_health_endpoints():
    """Test health and status endpoints"""
    print("🔍 Testing Health Endpoints...")
    
    # Test root endpoint
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Root endpoint: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   API Version: {data.get('data', {}).get('version', 'N/A')}")
    
    # Test health check
    response = requests.get(f"{BASE_URL}/api/v1/health/")
    print(f"✅ Health check: {response.status_code}")
    
    # Test readiness
    response = requests.get(f"{BASE_URL}/api/v1/health/ready")
    print(f"✅ Readiness check: {response.status_code}")
    
    # Test status
    response = requests.get(f"{BASE_URL}/api/v1/health/status")
    print(f"✅ Status check: {response.status_code}")

def test_fitness_goals():
    """Test fitness goals endpoint"""
    print("\n🔍 Testing Fitness Goals...")
    
    response = requests.get(f"{BASE_URL}/api/v1/meals/goals", headers=HEADERS)
    print(f"✅ Fitness goals: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        goals = data.get('data', {}).get('goals', [])
        print(f"   Available goals: {len(goals)}")
        for goal in goals:
            print(f"   - {goal['name']}: {goal['description']}")

def test_nutrition_rules():
    """Test nutrition rules endpoint"""
    print("\n🔍 Testing Nutrition Rules...")
    
    goals = ["muscle_gain", "weight_loss", "keto", "balanced"]
    
    for goal in goals:
        response = requests.get(f"{BASE_URL}/api/v1/meals/nutrition-rules/{goal}", headers=HEADERS)
        print(f"✅ Nutrition rules for {goal}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            rules = data.get('data', {}).get('rules', {})
            print(f"   Rules: {len(rules)} categories")

def test_meal_search():
    """Test meal search functionality"""
    print("\n🔍 Testing Meal Search...")
    
    # Test data for New York City
    test_request = {
        "lat": 40.7128,
        "lon": -74.0060,
        "goal": "muscle_gain",
        "cuisine": "japanese",
        "flavor_profile": "savory",
        "radius_miles": 1.24,
        "max_results": 3,
        "restaurant_limit": 3
    }
    
    print(f"   Testing with: {json.dumps(test_request, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/meals/find",
        json=test_request,
        headers=HEADERS
    )
    
    print(f"✅ Meal search: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        meals = data.get('data', {}).get('meals', [])
        print(f"   Found {len(meals)} meals")
        
        for i, meal in enumerate(meals[:2], 1):  # Show first 2 meals
            print(f"   Meal {i}: {meal.get('dish', 'N/A')}")
            print(f"     Restaurant: {meal.get('restaurant', 'N/A')}")
            print(f"     Score: {meal.get('relevance_score', 'N/A')}")
            print(f"     Tags: {meal.get('tags', [])}")
    else:
        print(f"   Error: {response.text}")

def test_nutrition_estimation():
    """Test nutrition estimation"""
    print("\n🔍 Testing Nutrition Estimation...")
    
    test_request = {
        "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
        "serving_size": "1 serving"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/nutrition/estimate",
        json=test_request,
        headers=HEADERS
    )
    
    print(f"✅ Nutrition estimation: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        nutrition = data.get('data', {}).get('nutrition', {})
        print(f"   Calories: {nutrition.get('calories', 'N/A')}")
        print(f"   Protein: {nutrition.get('protein', 'N/A')}g")
        print(f"   Carbs: {nutrition.get('carbs', 'N/A')}g")
        print(f"   Fat: {nutrition.get('fat', 'N/A')}g")

def test_freeform_search():
    """Test freeform search"""
    print("\n🔍 Testing Freeform Search...")
    
    test_request = {
        "query": "show me low-carb lunch near me",
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/meals/freeform-search",
        json=test_request,
        headers=HEADERS
    )
    
    print(f"✅ Freeform search: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        meals = data.get('data', {}).get('meals', [])
        print(f"   Found {len(meals)} meals from freeform search")

def test_api_documentation():
    """Test API documentation endpoints"""
    print("\n🔍 Testing API Documentation...")
    
    # Test Swagger UI
    response = requests.get(f"{BASE_URL}/docs")
    print(f"✅ Swagger UI: {response.status_code}")
    
    # Test OpenAPI schema
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"✅ OpenAPI schema: {response.status_code}")
    
    # Test ReDoc
    response = requests.get(f"{BASE_URL}/redoc")
    print(f"✅ ReDoc: {response.status_code}")

def test_error_handling():
    """Test error handling"""
    print("\n🔍 Testing Error Handling...")
    
    # Test invalid request
    invalid_request = {
        "lat": "invalid",
        "lon": "invalid",
        "goal": "invalid_goal"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/meals/find",
        json=invalid_request,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"✅ Invalid request handling: {response.status_code}")
    
    # Test 404
    response = requests.get(f"{BASE_URL}/api/v1/nonexistent")
    print(f"✅ 404 handling: {response.status_code}")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Good Eats MVP API Tests")
    print("=" * 50)
    
    try:
        test_health_endpoints()
        test_fitness_goals()
        test_nutrition_rules()
        test_meal_search()
        test_nutrition_estimation()
        test_freeform_search()
        test_api_documentation()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    run_all_tests() 