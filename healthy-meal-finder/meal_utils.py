# meal_utils.py

def score_meal(meal, rules):
    """
    Assigns a score based on how well the meal fits the nutrition rules.
    """
    score = 0

    if "max_calories" in rules and meal["calories"] <= rules["max_calories"]:
        score += 1
    if "min_protein" in rules and meal["protein"] >= rules["min_protein"]:
        score += 1
    if "max_carbs" in rules and meal["carbs"] <= rules["max_carbs"]:
        score += 1
    if "min_fat" in rules and meal["fat"] >= rules["min_fat"]:
        score += 1

    return score

def filter_by_distance(meals, max_distance):
    """
    Filters meals based on distance (in miles).
    """
    return [meal for meal in meals if meal["distance_miles"] <= max_distance]

def get_scored_meals(meals, rules):
    """
    Scores each meal and returns sorted list from best to worst match.
    """
    scored = []

    for meal in meals:
        score = score_meal(meal, rules)
        if score > 0:
            meal_copy = meal.copy()
            meal_copy["score"] = score
            scored.append(meal_copy)

    # Sort descending by score
    scored.sort(key=lambda m: m["score"], reverse=True)
    return scored
