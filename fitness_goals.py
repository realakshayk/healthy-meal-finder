# fitness_goals.py

def get_nutrition_rules(goal: str) -> dict:
    """
    Returns nutrition rules for a given fitness goal.
    Example: {"min_protein": 25, "max_calories": 700}
    """
    goal = goal.lower()

    if goal == "muscle_gain":
        return {
            "min_protein": 25,
            "max_calories": 800,
            "max_carbs": 60
        }
    elif goal == "weight_loss":
        return {
            "max_calories": 500,
            "max_carbs": 40,
            "min_protein": 15
        }
    elif goal == "keto":
        return {
            "max_carbs": 20,
            "min_fat": 30
        }
    else:
        # Default: balanced diet
        return {
            "max_calories": 700
        }
