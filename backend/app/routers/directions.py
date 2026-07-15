from fastapi import APIRouter, HTTPException, Query

from app.schemas import DirectionsResponse
from app.services.directions import DirectionsError, get_directions

router = APIRouter(prefix="/directions", tags=["directions"])


@router.get("/", response_model=DirectionsResponse)
def fetch_directions(
    origin_lat: float = Query(...),
    origin_lng: float = Query(...),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
):
    try:
        return get_directions(origin_lat, origin_lng, dest_lat, dest_lng)
    except DirectionsError as e:
        raise HTTPException(status_code=502, detail=str(e))
