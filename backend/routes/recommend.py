import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.recommendation_service import build_recommendation

router = APIRouter()
logger = logging.getLogger(__name__)


class RecommendRequest(BaseModel):
    location: str
    land_size: float
    last_crop: str | None = None


@router.post("/recommend")
def recommend(request: RecommendRequest):
    try:
        return build_recommendation(request.location, request.land_size, request.last_crop)
    except Exception:
        logger.exception("Failed to build recommendation for %s", request.location)
        raise HTTPException(status_code=503, detail="Could not build a recommendation right now, please retry.")
