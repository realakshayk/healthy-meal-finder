# core/dependencies.py

from fastapi import Depends, HTTPException, status, Header, Request
from typing import Optional
import logging
import os
from core.rate_limiter import check_rate_limit, get_rate_limit_status, get_partner_plan

logger = logging.getLogger(__name__)

# Example: allowed API keys (in production, use a database or env/config)
ALLOWED_API_KEYS = set(os.getenv("ALLOWED_API_KEYS", "testkey123,partnerkey456").split(","))

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

async def get_api_key(x_api_key: Optional[str] = Header(None), request: Request = None):
    """
    Dependency to require and validate an API key from the X-API-Key header.
    Also enforces per-partner rate limiting and attaches partner info to request.state.
    """
    if not x_api_key or x_api_key not in ALLOWED_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Set X-API-Key header.",
            headers={"WWW-Authenticate": "API-Key"}
        )
    partner_id = x_api_key
    if not check_rate_limit(partner_id):
        status_info = get_rate_limit_status(partner_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for partner '{partner_id}'. Plan: {status_info['plan']}, Used: {status_info['used']}, Limit: {status_info['limit']}",
        )
    # Attach partner info to request.state for downstream use
    if request is not None:
        request.state.partner_id = partner_id
        request.state.partner_plan = get_partner_plan(partner_id)
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