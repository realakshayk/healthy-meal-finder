import pytest
from meal_utils import score_meal, filter_by_distance, get_scored_meals

@pytest.fixture
def mock_meals():
    return [
        {"dish": "Chicken Bowl", "calories": 500, "protein": 35, "carbs": 40, "fat": 15, "distance_miles": 1.0},
        {"dish": "Salmon Salad", "calories": 400, "protein": 30, "carbs": 10, "fat": 25, "distance_miles": 2.5},
        {"dish": "Veggie Wrap", "calories": 350, "protein": 10, "carbs": 50, "fat": 8, "distance_miles": 4.0},
        {"dish": "Keto Plate", "calories": 600, "protein": 25, "carbs": 8, "fat": 35, "distance_miles": 0.5},
    ]

@pytest.fixture
def muscle_gain_rules():
    return {"min_protein": 25, "max_calories": 800, "max_carbs": 60}

@pytest.fixture
def keto_rules():
    return {"max_carbs": 20, "min_fat": 30}


def test_score_meal_muscle_gain(mock_meals, muscle_gain_rules):
    scores = [score_meal(meal, muscle_gain_rules) for meal in mock_meals]
    assert scores == [3, 3, 1, 2]

def test_score_meal_keto(mock_meals, keto_rules):
    scores = [score_meal(meal, keto_rules) for meal in mock_meals]
    assert scores == [0, 1, 0, 2]

def test_filter_by_distance(mock_meals):
    filtered = filter_by_distance(mock_meals, 2.0)
    assert len(filtered) == 2
    assert all(meal["distance_miles"] <= 2.0 for meal in filtered)

def test_get_scored_meals_sorted(mock_meals, muscle_gain_rules):
    scored = get_scored_meals(mock_meals, muscle_gain_rules)
    assert [m["dish"] for m in scored] == ["Chicken Bowl", "Salmon Salad", "Keto Plate", "Veggie Wrap"]
    assert [m["score"] for m in scored] == [3, 3, 2, 1] 