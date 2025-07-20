import pytest
from core.goal_matcher import GoalMatcher

goal_matcher = GoalMatcher()

def test_exact_match():
    goal, confidence = goal_matcher.match_goal("muscle gain")
    assert goal == "muscle_gain"
    assert confidence == 100

def test_fuzzy_match():
    goal, confidence = goal_matcher.match_goal("musle gain")
    assert goal == "muscle_gain"
    assert confidence >= 80

def test_synonym_match():
    goal, confidence = goal_matcher.match_goal("lean bulk")
    assert goal == "muscle_gain"
    assert confidence >= 80

def test_weight_loss_variants():
    for variant in ["lose weight", "fat loss", "cutting"]:
        goal, confidence = goal_matcher.match_goal(variant)
        assert goal == "weight_loss"
        assert confidence >= 80

def test_keto_variants():
    for variant in ["keto", "low carb", "ketogenic diet"]:
        goal, confidence = goal_matcher.match_goal(variant)
        assert goal == "keto"
        assert confidence >= 80

def test_balanced_variants():
    for variant in ["balanced", "healthy eating", "maintenance"]:
        goal, confidence = goal_matcher.match_goal(variant)
        assert goal == "balanced"
        assert confidence >= 80

def test_no_match():
    goal, confidence = goal_matcher.match_goal("random goal")
    assert goal is None
    assert confidence == 0

def test_suggestions():
    suggestions = goal_matcher.get_suggestions("musle gaim")
    assert any(s[0] == "muscle_gain" for s in suggestions)
    assert len(suggestions) > 0 