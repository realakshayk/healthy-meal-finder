# test_fuzzy_matching.py

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_goal_matching():
    """Test the fuzzy goal matching functionality."""
    print("Testing Fuzzy Goal Matching")
    print("=" * 40)
    
    # Test cases with various inputs
    test_cases = [
        # Muscle gain variations
        "musle gain",
        "lean bulk", 
        "bulking",
        "muscle building",
        "gain muscle",
        "put on muscle",
        "get bigger",
        "muscle growth",
        "bodybuilding",
        "strength training",
        
        # Weight loss variations
        "lose weight",
        "loose weight",  # Common misspelling
        "fat loss",
        "burn fat",
        "slim down",
        "get lean",
        "cut",
        "cutting",
        "diet",
        "weight reduction",
        "shed pounds",
        
        # Keto variations
        "keto",
        "ketogenic",
        "low carb",
        "keto diet",
        "ketosis",
        "keto lifestyle",
        "low carbohydrate",
        
        # Balanced variations
        "balanced",
        "healthy eating",
        "maintenance",
        "general health",
        "wellness",
        "healthy lifestyle",
        "balanced nutrition",
        
        # Edge cases
        "muscle",  # Partial match
        "gain",    # Partial match
        "weight",  # Partial match
        "diet",    # Ambiguous
        "invalid goal",  # No match
        "",        # Empty
        "   ",     # Whitespace only
    ]
    
    for user_input in test_cases:
        print(f"\n--- Testing: '{user_input}' ---")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/meals/match-goal/{user_input}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data['data']
                    print(f"✅ Matched to: {result['matched_goal']} ({result['goal_name']})")
                    print(f"   Confidence: {result['confidence']}%")
                    print(f"   User input: '{result['user_input']}'")
                    
                    if result.get('suggestions'):
                        print(f"   Suggestions: {len(result['suggestions'])} available")
                else:
                    print(f"❌ No match found")
                    print(f"   Error: {data.get('error')}")
                    print(f"   Detail: {data.get('detail')}")
            else:
                print(f"❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)

def test_find_meals_with_natural_language():
    """Test the find meals endpoint with natural language inputs."""
    print("\nTesting Find Meals with Natural Language")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Muscle Gain Variations",
            "inputs": ["musle gain", "lean bulk", "bulking", "muscle building"],
            "lat": 40.7128,
            "lon": -74.0060,
            "radius_miles": 5.0
        },
        {
            "name": "Weight Loss Variations", 
            "inputs": ["lose weight", "fat loss", "cutting", "slim down"],
            "lat": 34.0522,
            "lon": -118.2437,
            "radius_miles": 3.0
        },
        {
            "name": "Keto Variations",
            "inputs": ["keto", "ketogenic", "low carb", "keto diet"],
            "lat": 41.8781,
            "lon": -87.6298,
            "radius_miles": 4.0
        },
        {
            "name": "Balanced Variations",
            "inputs": ["balanced", "healthy eating", "maintenance", "wellness"],
            "lat": 29.7604,
            "lon": -95.3698,
            "radius_miles": 3.5
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        for goal_input in test_case['inputs']:
            print(f"\nTesting: '{goal_input}'")
            
            payload = {
                "lat": test_case["lat"],
                "lon": test_case["lon"],
                "goal": goal_input,
                "radius_miles": test_case["radius_miles"],
                "max_results": 2
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1/meals/find",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        meals_data = data['data']
                        print(f"✅ Success: {data.get('message')}")
                        print(f"   Matched goal: {meals_data.get('goal')}")
                        print(f"   Meals found: {meals_data.get('total_found')}")
                    else:
                        print(f"❌ Failed: {data.get('error')}")
                else:
                    print(f"❌ Request failed: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")

def test_fitness_goals_with_synonyms():
    """Test the fitness goals endpoint to see synonyms."""
    print("\nTesting Fitness Goals with Synonyms")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/meals/goals")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                goals = data['data'].get('goals', [])
                print(f"Found {len(goals)} fitness goals:")
                
                for goal in goals:
                    print(f"\n📋 {goal['name']} ({goal['id']})")
                    print(f"   Description: {goal['description']}")
                    print(f"   Synonyms ({goal['total_synonyms']} total):")
                    
                    # Show first 5 synonyms
                    for synonym in goal['synonyms'][:5]:
                        print(f"     - {synonym}")
                    
                    if len(goal['synonyms']) > 5:
                        print(f"     ... and {len(goal['synonyms']) - 5} more")
            else:
                print(f"❌ Failed: {data.get('error')}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\nTesting Error Handling")
    print("=" * 30)
    
    invalid_inputs = [
        "invalid goal",
        "random text",
        "xyz",
        "muscle gain invalid",
        "weight loss extra words"
    ]
    
    for invalid_input in invalid_inputs:
        print(f"\nTesting invalid input: '{invalid_input}'")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/meals/match-goal/{invalid_input}")
            
            if response.status_code == 400:
                data = response.json()
                print(f"✅ Properly rejected with error: {data.get('error')}")
                print(f"   Detail: {data.get('detail')}")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Fuzzy Natural Language Matching")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        test_goal_matching()
        test_find_meals_with_natural_language()
        test_fitness_goals_with_synonyms()
        test_error_handling()
        
        print("\n✅ All fuzzy matching tests completed!")
        print("\n🎯 The API now supports natural language input for fitness goals!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 