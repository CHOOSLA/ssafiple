from typing import List
from pydantic import BaseModel


class RoutePoint(BaseModel):
    lat: float
    lng: float


class DirectionsResponse(BaseModel):
    path: List[RoutePoint]
    duration: int  # 예상 소요 시간 (초)
    distance: int  # 이동 거리 (미터)
