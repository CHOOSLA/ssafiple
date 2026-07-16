"""길찾기(경로 안내) 서비스 계층.

- 자동차: 카카오모빌리티 Directions API
- 대중교통: ODsay 대중교통 길찾기 API

REST API 키를 서버에서만 다뤄야 하므로, 프론트는 이 서비스를 감싼 라우터만 호출합니다.
"""
from typing import Dict, List
from urllib.parse import unquote

import httpx

from app.core.config import settings

KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"
ODSAY_TRANSIT_URL = "https://api.odsay.com/v1/api/searchPubTransPathT"


class DirectionsError(Exception):
    """길찾기 조회 실패 시 라우터가 502로 변환할 예외."""


def get_car_directions(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict:
    if not settings.KAKAO_REST_API_KEY:
        raise DirectionsError("KAKAO_REST_API_KEY가 설정되지 않았습니다.")

    # 카카오 좌표 파라미터는 "경도,위도"(x,y) 순서
    params = {
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
        "priority": "RECOMMEND",
        "alternatives": "true",
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
    ok_routes = [route for route in routes if route.get("result_code") == 0]
    if not ok_routes:
        message = routes[0].get("result_msg") if routes else None
        raise DirectionsError(message or "경로를 찾을 수 없습니다.")

    candidates: List[Dict] = []
    for idx, route in enumerate(ok_routes[:3]):
        summary = route.get("summary", {})

        path: List[Dict[str, float]] = []
        for section in route.get("sections", []):
            for road in section.get("roads", []):
                vertexes = road.get("vertexes", [])
                # vertexes: [lng1, lat1, lng2, lat2, ...] 평탄화된 좌표열
                for i in range(0, len(vertexes) - 1, 2):
                    path.append({"lng": vertexes[i], "lat": vertexes[i + 1]})

        candidates.append({
            "label": "추천 경로" if idx == 0 else f"대안 경로 {idx}",
            "path": path,
            "duration": summary.get("duration", 0),
            "distance": summary.get("distance", 0),
        })

    return {"candidates": candidates}


def get_transit_directions(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict:
    if not settings.ODSAY_API_KEY:
        raise DirectionsError("ODSAY_API_KEY가 설정되지 않았습니다.")

    params = {
        "SX": origin_lng,
        "SY": origin_lat,
        "EX": dest_lng,
        "EY": dest_lat,
        "OPT": 0,
        # ODsay 키에 이미 percent-encoding된 문자가 포함될 수 있어, 한 번 디코드해서
        # httpx가 다시 정상적으로 인코딩하도록 한다 (이중 인코딩 방지).
        "apiKey": unquote(settings.ODSAY_API_KEY),
    }

    try:
        response = httpx.get(ODSAY_TRANSIT_URL, params=params, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise DirectionsError(f"ODsay 길찾기 API 오류 (status={e.response.status_code})") from e
    except httpx.HTTPError as e:
        raise DirectionsError("ODsay 길찾기 API 요청에 실패했습니다.") from e

    data = response.json()

    error = data.get("error")
    if error:
        message = error.get("msg") if isinstance(error, dict) else str(error)
        raise DirectionsError(message or "대중교통 경로를 찾을 수 없습니다.")

    result = data.get("result")
    if not result:
        raise DirectionsError("대중교통 경로를 찾을 수 없습니다.")

    paths = result.get("path") or []
    paths = sorted(paths, key=lambda p: p.get("info", {}).get("totalTime", 0))[:3]

    candidates: List[Dict] = []
    for path in paths:
        info = path.get("info", {})

        segments: List[Dict] = []
        for sub in path.get("subPath", []):
            traffic_type = sub.get("trafficType")
            if traffic_type == 1:
                mode = "subway"
                lane = (sub.get("lane") or [{}])[0]
                label = lane.get("name")
            elif traffic_type == 2:
                mode = "bus"
                lane = (sub.get("lane") or [{}])[0]
                label = lane.get("busNo")
            else:
                mode = "walk"
                label = None

            segments.append({
                "mode": mode,
                "label": label,
                "start_name": sub.get("startName", ""),
                "end_name": sub.get("endName", ""),
                "duration": sub.get("sectionTime", 0) * 60,
                "distance": sub.get("distance", 0),
                "path": [
                    {"lat": float(sub.get("startY", 0)), "lng": float(sub.get("startX", 0))},
                    {"lat": float(sub.get("endY", 0)), "lng": float(sub.get("endX", 0))},
                ],
            })

        candidates.append({
            "duration": info.get("totalTime", 0) * 60,
            "distance": info.get("totalDistance", 0),
            "transfer_count": info.get("busTransitCount", 0) + info.get("subwayTransitCount", 0),
            "walk_distance": info.get("totalWalk", 0),
            "segments": segments,
        })

    return {"candidates": candidates}
