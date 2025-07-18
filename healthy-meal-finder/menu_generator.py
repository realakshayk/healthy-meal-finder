# menu_generator.py

from menu_generator import generate_mock_menu
from fitness_goals import get_nutrition_rules
from meal_utils import get_scored_meals

import random

def generate_mock_menu(restaurant_name):
    base_items = [
        "Grilled Chicken Bowl",
        "Avocado & Quinoa Salad",
        "Tofu Power Bowl",
        "Steak & Veggie Wrap",
        "Turkey Lettuce Wraps",
        "Low-Carb Chicken Stir Fry",
        "Keto Beef Skillet",
        "Baked Salmon with Greens",
        "Protein Pancakes",
        "Greek Yogurt & Berries"
    ]

    menu = []
    for item in random.sample(base_items, k=5):
        menu.append({
            "restaurant": restaurant_name,
            "dish": item,
            "description": f"{item} with fresh ingredients",
            "calories": random.randint(350, 800),
            "protein": random.randint(20, 45),
            "carbs": random.randint(10, 70),
            "fat": random.randint(10, 35),
        })

    return menu
