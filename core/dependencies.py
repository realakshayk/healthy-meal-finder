# core/dependencies.py

from fastapi import Depends, HTTPException, status, Header, Request
from typing import Optional
import logging
import os
from core.rate_limiter import check_rate_limit, get_rate_limit_status, get_partner_plan
from core.error_handlers import InvalidAPIKeyException, RateLimitExceededException
import yaml

logger = logging.getLogger(__name__)

# Load allowed API keys from .env or config.yml (with per-key roles/permissions)
def load_allowed_api_keys():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
    config_path = os.path.abspath(config_path)
    allowed_keys = {}
    # Try config.yml first
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            for key, meta in config.get('allowed_api_keys', {}).items():
                allowed_keys[key] = meta or {"role": "partner"}
    else:
        # Fallback to .env (comma-separated keys, all as 'partner')
        keys = os.getenv("ALLOWED_API_KEYS", "testkey123,partnerkey456").split(",")
        for key in keys:
            allowed_keys[key.strip()] = {"role": "partner"}
    return allowed_keys

ALLOWED_API_KEYS = load_allowed_api_keys()

def get_api_version() -> str:
    """
    Get the current API version.
    
    Returns:
        Current API version string
    """
    return "v1"

def get_partner_id(partner_id: Optional[str] = None) -> Optional[str]:
    """
    Get partner ID from request headers or query parameters.
    
    Args:
        partner_id: Partner ID from query parameter
        
    Returns:
        Partner ID if provided, None otherwise
    """
    return partner_id

async def get_api_key(request: Request, x_api_key: Optional[str] = Header(None)):
    """
    Dependency to require and validate an API key from the X-API-Key header.
    Also enforces per-partner rate limiting.
    Attaches partner role/permissions to request.state for downstream use.
    """
    if not x_api_key or x_api_key not in ALLOWED_API_KEYS:
        raise InvalidAPIKeyException()
    # Attach partner info to request.state
    request.state.partner_info = ALLOWED_API_KEYS[x_api_key]
    partner_id = x_api_key
    if not check_rate_limit(partner_id):
        status_info = get_rate_limit_status(partner_id)
        raise RateLimitExceededException(
            partner_id, 
            status_info['plan'], 
            status_info['used'], 
            status_info['limit']
        )
    return x_api_key

def validate_api_key(api_key: Optional[str] = None) -> bool:
    """
    Validate API key for partner authentication.
    
    Args:
        api_key: API key from request headers
        
    Returns:
        True if API key is valid, False otherwise
    """
    # TODO: Implement proper API key validation
    # For now, return True to allow all requests
    return True

def get_rate_limit_info(partner_id: Optional[str] = Depends(get_partner_id)) -> dict:
    """
    Get rate limiting information for the partner.
    
    Args:
        partner_id: Partner ID from dependency injection
        
    Returns:
        Dictionary with rate limit information
    """
    # TODO: Implement proper rate limiting
    return {
        "requests_per_minute": 100,
        "requests_per_hour": 1000,
        "partner_id": partner_id
    } 