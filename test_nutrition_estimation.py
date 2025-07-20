# test_nutrition_estimation.py

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_single_nutrition_estimation():
    """Test single meal nutrition estimation."""
    print("Testing Single Nutrition Estimation")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Protein-rich meal",
            "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
            "serving_size": "1 serving"
        },
        {
            "name": "Salad with protein",
            "meal_description": "Caesar salad with grilled salmon and avocado",
            "serving_size": "1 large bowl"
        },
        {
            "name": "Vegetarian option",
            "meal_description": "Buddha bowl with chickpeas, brown rice, and mixed vegetables",
            "serving_size": "1 bowl"
        },
        {
            "name": "High-carb meal",
            "meal_description": "Pasta with marinara sauce and meatballs",
            "serving_size": "1 plate"
        },
        {
            "name": "Low-carb option",
            "meal_description": "Grilled salmon with steamed broccoli and butter",
            "serving_size": "1 serving"
        },
        {
            "name": "Breakfast item",
            "meal_description": "Oatmeal with berries, nuts, and honey",
            "serving_size": "1 cup"
        },
        {
            "name": "Fast food style",
            "meal_description": "Burger with fries and soda",
            "serving_size": "1 meal"
        },
        {
            "name": "Healthy snack",
            "meal_description": "Greek yogurt with granola and fresh fruit",
            "serving_size": "1 cup"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Meal: {test_case['meal_description']}")
        print(f"Serving: {test_case['serving_size']}")
        
        payload = {
            "meal_description": test_case["meal_description"],
            "serving_size": test_case["serving_size"]
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/nutrition/estimate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data['data']
                    nutrition = result['nutrition']
                    validation = result['validation']
                    
                    print(f"✅ Success: {data.get('message')}")
                    print(f"   Method: {result.get('estimation_method')}")
                    print(f"   Calories: {nutrition['calories']}")
                    print(f"   Protein: {nutrition['protein']}g")
                    print(f"   Carbs: {nutrition['carbs']}g")
                    print(f"   Fat: {nutrition['fat']}g")
                    print(f"   Valid: {validation['is_valid']}")
                    print(f"   Validation: {validation['message']}")
                else:
                    print(f"❌ Failed: {data.get('error')}")
            else:
                print(f"❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)

def test_batch_nutrition_estimation():
    """Test batch nutrition estimation."""
    print("\nTesting Batch Nutrition Estimation")
    print("=" * 40)
    
    meals = [
        {
            "meal_description": "Grilled chicken breast with quinoa",
            "serving_size": "1 serving"
        },
        {
            "meal_description": "Caesar salad with grilled salmon",
            "serving_size": "1 large bowl"
        },
        {
            "meal_description": "Buddha bowl with chickpeas",
            "serving_size": "1 bowl"
        },
        {
            "meal_description": "Pasta with marinara sauce",
            "serving_size": "1 plate"
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/nutrition/estimate-batch",
            json=meals
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"✅ Success: {data.get('message')}")
                print(f"   Method: {result.get('estimation_method')}")
                print(f"   Total meals: {result.get('total_meals')}")
                
                for i, meal in enumerate(result['meals'], 1):
                    nutrition = meal['nutrition']
                    print(f"\n   Meal {i}: {meal['meal_description']}")
                    print(f"     Calories: {nutrition['calories']}")
                    print(f"     Protein: {nutrition['protein']}g")
                    print(f"     Carbs: {nutrition['carbs']}g")
                    print(f"     Fat: {nutrition['fat']}g")
            else:
                print(f"❌ Failed: {data.get('error')}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_nutrition_validation():
    """Test nutrition validation endpoint."""
    print("\nTesting Nutrition Validation")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Valid nutrition",
            "calories": 485,
            "protein": 34,
            "carbs": 29,
            "fat": 21
        },
        {
            "name": "High calorie meal",
            "calories": 1200,
            "protein": 45,
            "carbs": 80,
            "fat": 60
        },
        {
            "name": "Low calorie meal",
            "calories": 200,
            "protein": 15,
            "carbs": 20,
            "fat": 8
        },
        {
            "name": "Invalid - too high calories",
            "calories": 3000,
            "protein": 50,
            "carbs": 100,
            "fat": 80
        },
        {
            "name": "Invalid - calorie mismatch",
            "calories": 1000,
            "protein": 10,
            "carbs": 10,
            "fat": 10
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/nutrition/validate/{test_case['calories']}/{test_case['protein']}/{test_case['carbs']}/{test_case['fat']}"
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data['data']
                    validation = result['validation']
                    
                    print(f"✅ Success: {data.get('message')}")
                    print(f"   Valid: {validation['is_valid']}")
                    print(f"   Message: {validation['message']}")
                    print(f"   Calculated calories: {result.get('calculated_calories')}")
                else:
                    print(f"❌ Failed: {data.get('error')}")
            else:
                print(f"❌ Request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_error_handling():
    """Test error handling for nutrition endpoints."""
    print("\nTesting Error Handling")
    print("=" * 30)
    
    # Test empty meal description
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/nutrition/estimate",
            json={"meal_description": "", "serving_size": "1 serving"}
        )
        print(f"Empty description status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Properly rejected: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test empty batch
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/nutrition/estimate-batch",
            json=[]
        )
        print(f"Empty batch status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Properly rejected: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test invalid nutrition values
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/nutrition/validate/-100/50/50/50"
        )
        print(f"Invalid nutrition status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_estimation_methods():
    """Test different estimation methods (OpenAI vs fallback)."""
    print("\nTesting Estimation Methods")
    print("=" * 30)
    
    # Test with OpenAI available
    test_meal = "Grilled chicken breast with quinoa and roasted vegetables"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/nutrition/estimate",
            json={
                "meal_description": test_meal,
                "serving_size": "1 serving"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                method = result.get('estimation_method')
                print(f"✅ Estimation method: {method}")
                
                if method == "openai":
                    print("   Using OpenAI for estimation")
                else:
                    print("   Using fallback keyword-based estimation")
                    print("   (OpenAI API key not configured)")
            else:
                print(f"❌ Failed: {data.get('error')}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Nutrition Estimation API")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        test_single_nutrition_estimation()
        test_batch_nutrition_estimation()
        test_nutrition_validation()
        test_error_handling()
        test_estimation_methods()
        
        print("\n✅ All nutrition estimation tests completed!")
        print("\n🎯 The API now supports AI-powered nutrition estimation!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 