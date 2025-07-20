# api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from core.api_key_manager import rotate_api_key, is_admin
from schemas.responses import ApiResponse
from core.dependencies import get_api_key

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.post(
    "/rotate-api-key/{partner_id}",
    response_model=ApiResponse,
    summary="Rotate a partner's API key (admin only)",
    description="Securely generate and set a new API key for the given partner. Admin only.",
)
async def rotate_partner_api_key(
    partner_id: str,
    x_api_key: str = Depends(get_api_key)
):
    if not is_admin(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    new_key = rotate_api_key(partner_id)
    return ApiResponse(
        success=True,
        data={"partner_id": partner_id, "new_api_key": new_key},
        message=f"API key for partner '{partner_id}' rotated successfully.",
        api_version="v1"
    ) 