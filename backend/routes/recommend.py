from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.recommendation_service import build_recommendation

router = APIRouter()


class RecommendRequest(BaseModel):
    location: str
    land_size: float
    last_crop: str | None = None


@router.post("/recommend")
def recommend(request: RecommendRequest):
    return build_recommendation(request.location, request.land_size, request.last_crop)
