# api/v1/endpoints/partners.py
from fastapi import APIRouter, Query, Depends
from schemas.responses import ApiResponse
from core.dependencies import get_api_key

router = APIRouter(
    prefix="/partners",
    tags=["partners"],
)

@router.get(
    "/stats",
    response_model=ApiResponse,
    summary="Get partner usage and performance stats (mocked)",
    description="Returns mocked usage and performance metrics for a given partner ID.",
)
async def get_partner_stats(
    partner_id: str = Query(..., description="Partner ID to fetch stats for"),
    x_api_key: str = Depends(get_api_key)
):
    # Mocked stats
    stats = {
        "partner_id": partner_id,
        "requests_today": 42,
        "requests_this_month": 1234,
        "average_response_time_ms": 210,
        "success_rate": 0.98,
        "top_endpoints": [
            {"endpoint": "/api/v1/meals/find", "count": 30},
            {"endpoint": "/api/v1/nutrition/estimate", "count": 12}
        ],
        "last_request": "2024-06-10T14:23:00Z"
    }
    return ApiResponse(
        success=True,
        data=stats,
        message=f"Mocked stats for partner {partner_id}",
        api_version="v1"
    ) 