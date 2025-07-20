# api/v1/router.py

from fastapi import APIRouter, Depends
from api.v1.endpoints import meals, health, nutrition, admin, partners
from core.dependencies import get_api_key

# Create the main v1 API router
api_router = APIRouter(prefix="/api/v1")

# Require API key for all endpoints except health
api_router.include_router(meals.router, prefix="/meals", tags=["meals"], dependencies=[Depends(get_api_key)])
api_router.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"], dependencies=[Depends(get_api_key)])
api_router.include_router(health.router, prefix="/health", tags=["health"]) # health endpoints are public 
api_router.include_router(admin.router, prefix="/admin", tags=["admin"]) # admin endpoints 
api_router.include_router(partners.router, prefix="/partners", tags=["partners"]) # partners endpoints 