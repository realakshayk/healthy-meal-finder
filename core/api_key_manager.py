# core/api_key_manager.py
import secrets
from typing import Dict
import threading

# In-memory API key store for demo (replace with DB in production)
_api_keys = {
    "partner123": "testkey123",
    "partner456": "prokey456",
    "admin": "adminkey789"
}
_lock = threading.Lock()


def get_api_key(partner_id: str) -> str:
    with _lock:
        return _api_keys.get(partner_id)

def set_api_key(partner_id: str, new_key: str):
    with _lock:
        _api_keys[partner_id] = new_key

def rotate_api_key(partner_id: str) -> str:
    """
    Securely generate and set a new API key for the given partner.
    Returns the new key.
    """
    new_key = secrets.token_urlsafe(32)
    set_api_key(partner_id, new_key)
    return new_key

def is_admin(api_key: str) -> bool:
    # For demo, admin is 'adminkey789'
    return api_key == _api_keys.get("admin") 