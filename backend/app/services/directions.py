"""카카오모빌리티 자동차 길찾기(FR 미정의, [Could] 경로 안내) 서비스 계층.

REST API 키를 서버에서만 다뤄야 하므로, 프론트는 이 서비스를 감싼 라우터만 호출합니다.
"""
from typing import Dict, List

import httpx

from app.core.config import settings

KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


class DirectionsError(Exception):
    """길찾기 조회 실패 시 라우터가 502로 변환할 예외."""


def get_directions(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict:
    if not settings.KAKAO_REST_API_KEY:
        raise DirectionsError("KAKAO_REST_API_KEY가 설정되지 않았습니다.")

    # 카카오 좌표 파라미터는 "경도,위도"(x,y) 순서
    params = {
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
        "priority": "RECOMMEND",
    }
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}

    try:
        response = httpx.get(KAKAO_DIRECTIONS_URL, params=params, headers=headers, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise DirectionsError(f"카카오 길찾기 API 오류 (status={e.response.status_code})") from e
    except httpx.HTTPError as e:
        raise DirectionsError("카카오 길찾기 API 요청에 실패했습니다.") from e

    data = response.json()
    routes = data.get("routes") or []
    if not routes or routes[0].get("result_code") != 0:
        message = routes[0].get("result_msg") if routes else None
        raise DirectionsError(message or "경로를 찾을 수 없습니다.")

    route = routes[0]
    summary = route.get("summary", {})

    path: List[Dict[str, float]] = []
    for section in route.get("sections", []):
        for road in section.get("roads", []):
            vertexes = road.get("vertexes", [])
            # vertexes: [lng1, lat1, lng2, lat2, ...] 평탄화된 좌표열
            for i in range(0, len(vertexes) - 1, 2):
                path.append({"lng": vertexes[i], "lat": vertexes[i + 1]})

    return {
        "path": path,
        "duration": summary.get("duration", 0),
        "distance": summary.get("distance", 0),
    }
