# services/meal_service.py

import logging
from fitness_goals import get_nutrition_rules
from meal_utils import filter_by_distance, get_scored_meals
from mock_meals import mock_meals

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Can also use DEBUG for more detail

def find_meals(location: str, goal: str, radius_miles: float):
    """
    Handles all business logic for finding meals.
    """
    rules = get_nutrition_rules(goal)
    logger.info(f"[Goal] '{goal}' maps to nutrition rules: {rules}")

    nearby_meals = filter_by_distance(mock_meals, radius_miles)
    logger.info(f"[Filter] {len(nearby_meals)} meals within {radius_miles} miles.")

    scored_meals = get_scored_meals(nearby_meals, rules)
    logger.info(f"[Scoring] Returning {len(scored_meals)} scored meals.")

    for meal in scored_meals:
        meal["goal_match"] = goal

    return scored_meals
