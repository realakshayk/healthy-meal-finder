# core/rate_limiter.py
import time
import threading
import yaml
import os
from collections import defaultdict

# Load rate limit config from YAML file
RATE_LIMIT_CONFIG_PATH = os.getenv("RATE_LIMIT_CONFIG_PATH", "rate_limits.yaml")

def load_rate_limits():
    if os.path.exists(RATE_LIMIT_CONFIG_PATH):
        with open(RATE_LIMIT_CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    # Default config if file missing
    return {
        "free": {"daily": 100},
        "pro": {"daily": 10000},
        "default": {"daily": 100}
    }

RATE_LIMITS = load_rate_limits()

# partner_id -> {"plan": str, "used": int, "reset": timestamp}
_partner_usage = defaultdict(lambda: {"used": 0, "reset": 0, "plan": "free"})
_lock = threading.Lock()


def get_partner_plan(partner_id: str) -> str:
    # In production, fetch from DB or config
    # For demo, use partner_id as plan if matches, else 'free'
    if partner_id in RATE_LIMITS:
        return partner_id
    return "free"

def get_plan_limit(plan: str) -> int:
    return RATE_LIMITS.get(plan, RATE_LIMITS["default"]).get("daily", 100)


def check_rate_limit(partner_id: str) -> bool:
    """
    Returns True if under limit, False if exceeded.
    """
    now = int(time.time())
    with _lock:
        usage = _partner_usage[partner_id]
        plan = get_partner_plan(partner_id)
        limit = get_plan_limit(plan)
        # Reset daily at midnight UTC
        if now >= usage["reset"]:
            # Next reset at next UTC midnight
            t = time.gmtime(now)
            next_midnight = int(time.mktime((t.tm_year, t.tm_mon, t.tm_mday + 1, 0, 0, 0, 0, 0, 0)))
            usage["used"] = 0
            usage["reset"] = next_midnight
            usage["plan"] = plan
        if usage["used"] < limit:
            usage["used"] += 1
            return True
        return False

def get_rate_limit_status(partner_id: str) -> dict:
    with _lock:
        usage = _partner_usage[partner_id]
        plan = get_partner_plan(partner_id)
        limit = get_plan_limit(plan)
        return {
            "plan": plan,
            "used": usage["used"],
            "limit": limit,
            "reset": usage["reset"]
        } 