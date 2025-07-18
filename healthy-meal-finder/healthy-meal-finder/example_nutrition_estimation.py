# example_nutrition_estimation.py

"""
Example script demonstrating the nutrition estimation utility.

This script shows how to use the NutritionEstimator class directly
for estimating nutrition from meal descriptions.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.nutrition_estimator import NutritionEstimator

def main():
    """Demonstrate nutrition estimation functionality."""
    
    print("🍽️  Nutrition Estimation Example")
    print("=" * 50)
    
    # Initialize the nutrition estimator
    estimator = NutritionEstimator()
    
    # Test meal descriptions
    test_meals = [
        {
            "name": "Protein-rich meal",
            "description": "Grilled chicken breast with quinoa and roasted vegetables",
            "serving_size": "1 serving"
        },
        {
            "name": "Salad with protein",
            "description": "Caesar salad with grilled salmon and avocado",
            "serving_size": "1 large bowl"
        },
        {
            "name": "Vegetarian option",
            "description": "Buddha bowl with chickpeas, brown rice, and mixed vegetables",
            "serving_size": "1 bowl"
        },
        {
            "name": "High-carb meal",
            "description": "Pasta with marinara sauce and meatballs",
            "serving_size": "1 plate"
        },
        {
            "name": "Low-carb option",
            "description": "Grilled salmon with steamed broccoli and butter",
            "serving_size": "1 serving"
        },
        {
            "name": "Breakfast item",
            "description": "Oatmeal with berries, nuts, and honey",
            "serving_size": "1 cup"
        },
        {
            "name": "Fast food style",
            "description": "Burger with fries and soda",
            "serving_size": "1 meal"
        },
        {
            "name": "Healthy snack",
            "description": "Greek yogurt with granola and fresh fruit",
            "serving_size": "1 cup"
        }
    ]
    
    print(f"Using estimation method: {'OpenAI' if estimator.client else 'Fallback'}")
    if not estimator.client:
        print("Note: OpenAI API key not found, using fallback estimation")
    print()
    
    # Estimate nutrition for each meal
    for i, meal in enumerate(test_meals, 1):
        print(f"{i}. {meal['name']}")
        print(f"   Meal: {meal['description']}")
        print(f"   Serving: {meal['serving_size']}")
        
        # Estimate nutrition
        nutrition = estimator.estimate_nutrition(
            meal['description'],
            meal['serving_size']
        )
        
        # Validate the estimate
        is_valid, validation_message = estimator.validate_nutrition_estimate(nutrition)
        
        print(f"   📊 Nutrition Estimate:")
        print(f"      Calories: {nutrition['calories']}")
        print(f"      Protein: {nutrition['protein']}g")
        print(f"      Carbs: {nutrition['carbs']}g")
        print(f"      Fat: {nutrition['fat']}g")
        print(f"      Valid: {'✅' if is_valid else '❌'}")
        print(f"      Validation: {validation_message}")
        print()
    
    # Demonstrate batch estimation
    print("🔄 Batch Estimation Example")
    print("-" * 30)
    
    meal_descriptions = [
        "Grilled chicken breast with quinoa",
        "Caesar salad with grilled salmon",
        "Buddha bowl with chickpeas",
        "Pasta with marinara sauce"
    ]
    
    batch_results = estimator.estimate_nutrition_batch(meal_descriptions)
    
    for i, (description, nutrition) in enumerate(zip(meal_descriptions, batch_results), 1):
        print(f"{i}. {description}")
        print(f"   Calories: {nutrition['calories']}, Protein: {nutrition['protein']}g")
        print(f"   Carbs: {nutrition['carbs']}g, Fat: {nutrition['fat']}g")
        print()
    
    # Demonstrate validation
    print("🔍 Nutrition Validation Examples")
    print("-" * 30)
    
    test_nutrition_values = [
        {
            "name": "Valid nutrition",
            "calories": 485,
            "protein": 34,
            "carbs": 29,
            "fat": 21
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
    
    for test_case in test_nutrition_values:
        nutrition = {
            "calories": test_case["calories"],
            "protein": test_case["protein"],
            "carbs": test_case["carbs"],
            "fat": test_case["fat"]
        }
        
        is_valid, message = estimator.validate_nutrition_estimate(nutrition)
        
        print(f"{test_case['name']}:")
        print(f"   Calories: {nutrition['calories']}, Protein: {nutrition['protein']}g")
        print(f"   Carbs: {nutrition['carbs']}g, Fat: {nutrition['fat']}g")
        print(f"   Valid: {'✅' if is_valid else '❌'}")
        print(f"   Message: {message}")
        print()
    
    print("✅ Nutrition estimation example completed!")
    print("\n💡 Tips:")
    print("   - Set OPENAI_API_KEY environment variable for AI-powered estimation")
    print("   - Fallback estimation works without API key")
    print("   - Use batch estimation for multiple meals")
    print("   - Always validate nutrition estimates")

if __name__ == "__main__":
    main() 