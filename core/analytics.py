# core/analytics.py
from collections import Counter, defaultdict
from threading import Lock

# Thread-safe counters
_meal_counter = Counter()
_goal_counter = Counter()
_lock = Lock()

# Optionally, track per-partner or per-API-key usage
_partner_goal_counter = defaultdict(Counter)
_partner_meal_counter = defaultdict(Counter)


def log_meal_returned(meal_id: str, dish: str, partner: str = None):
    with _lock:
        _meal_counter[meal_id] += 1
        if partner:
            _partner_meal_counter[partner][meal_id] += 1

def log_goal_searched(goal: str, partner: str = None):
    with _lock:
        _goal_counter[goal] += 1
        if partner:
            _partner_goal_counter[partner][goal] += 1

def get_top_meals(n=10):
    with _lock:
        return _meal_counter.most_common(n)

def get_top_goals(n=10):
    with _lock:
        return _goal_counter.most_common(n)

def get_partner_stats(partner: str):
    with _lock:
        return {
            "meals": _partner_meal_counter[partner].most_common(10),
            "goals": _partner_goal_counter[partner].most_common(10)
        }

def get_all_stats():
    with _lock:
        return {
            "top_meals": get_top_meals(),
            "top_goals": get_top_goals(),
            "partner_stats": {k: get_partner_stats(k) for k in _partner_goal_counter.keys()}
        } 