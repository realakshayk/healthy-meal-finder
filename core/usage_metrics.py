# core/usage_metrics.py
import threading
import logging
from collections import defaultdict
from datetime import datetime

# Set up logging to file
logging.basicConfig(
    filename='usage_metrics.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

_usage_counts = defaultdict(lambda: defaultdict(int))  # api_key -> endpoint -> count
_lock = threading.Lock()

def log_usage(api_key: str, endpoint: str):
    with _lock:
        _usage_counts[api_key][endpoint] += 1
        count = _usage_counts[api_key][endpoint]
        logging.info(f"API_KEY={api_key} ENDPOINT={endpoint} COUNT={count}")

def get_usage_counts():
    with _lock:
        # Return a copy for inspection
        return {k: dict(v) for k, v in _usage_counts.items()} 