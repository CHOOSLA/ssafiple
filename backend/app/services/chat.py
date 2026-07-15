"""AI 챗봇(FR-CHT-01) 서비스 계층.

라우터는 HTTP 관심사(요청 검증, 상태 코드)만 담당하고,
프롬프트 조립 및 OpenAI 호출은 모두 이 모듈에서 처리합니다.
"""
import re
from typing import List, Tuple

import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Location
from app.schemas import ChatMessage

# 챗봇 답변에서 지도 이동/검색 연동에 사용할 장소 매칭 최대 개수
MAX_MATCHED_LOCATIONS = 3

# 메시지에서 장소명을 추출할 때 무시할 조사/상투어
_STOPWORDS = {"에서", "에게", "으로", "에는", "정도", "추천해줘", "추천", "알려줘", "있어", "있나요", "근처", "주변", "여행"}

# 카테고리 힌트 키워드 → locations.category 값 매핑 (이름 매칭 실패 시 보조 사용)
_CATEGORY_KEYWORDS = {
    "맛집": "음식점", "음식": "음식점", "먹을": "음식점", "카페": "음식점",
    "관광": "관광지", "명소": "관광지", "구경": "관광지",
    "전시": "문화시설", "박물관": "문화시설", "문화": "문화시설", "공연": "문화시설",
    "쇼핑": "쇼핑", "백화점": "쇼핑",
    "숙박": "숙박", "호텔": "숙박", "게스트하우스": "숙박",
}

SYSTEM_PROMPT = (
    "당신은 서울 여행 정보 커뮤니티 'SSAFIPLE'의 AI 여행 비서입니다. "
    "서울의 관광지 추천, 축제 안내, 맛집 위치, 커뮤니티 게시글 관련 질문에 한국어로 친절하고 간결하게 답변하세요. "
    "답변은 3~5문장 이내로 요약하고, 확실하지 않은 정보는 추측하지 말고 모른다고 밝히세요. "
    "서울 여행 안내와 무관한 질문에는 정중히 답변할 수 없다고 안내하세요."
)

DEMO_REPLY = (
    "[데모 모드] 현재 OpenAI API Key가 설정되지 않아 실제 답변을 생성할 수 없습니다.\n"
    "backend/.env 파일에 OPENAI_API_KEY를 입력한 뒤 서버를 다시 시작해 주세요."
)


def _extract_tokens(message: str) -> List[str]:
    """메시지에서 장소명 매칭 후보가 될 2글자 이상 단어를 추출합니다."""
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", message)
    return [w for w in words if w not in _STOPWORDS]


def find_matching_locations(db: Session, message: str, limit: int = MAX_MATCHED_LOCATIONS) -> List[Location]:
    """사용자 메시지에 등장하는 단어로 locations 테이블을 단순 키워드/이름 매칭합니다.

    1) 메시지 토큰이 장소명(name)에 부분 일치하면 우선 매칭.
    2) 이름 매칭이 하나도 없으면 카테고리 힌트 키워드(맛집→음식점 등)로 보조 매칭.
    """
    matched: dict[int, Location] = {}

    for token in _extract_tokens(message):
        if len(matched) >= limit:
            break
        rows = db.query(Location).filter(Location.name.like(f"%{token}%")).limit(limit).all()
        for loc in rows:
            matched.setdefault(loc.id, loc)

    if not matched:
        for keyword, category in _CATEGORY_KEYWORDS.items():
            if keyword in message:
                rows = db.query(Location).filter(Location.category == category).limit(limit).all()
                for loc in rows:
                    matched.setdefault(loc.id, loc)
                break

    return list(matched.values())[:limit]


def build_context(locations: List[Location]) -> str:
    """매칭된 장소 목록을 OpenAI 시스템 프롬프트에 주입할 컨텍스트 문자열로 조립합니다."""
    if not locations:
        return ""
    lines = [
        f"- {loc.name} ({loc.category or '기타'}): {loc.address or '주소 정보 없음'}"
        for loc in locations
    ]
    return "\n".join(lines)


def generate_reply(db: Session, message: str, history: List[ChatMessage]) -> Tuple[str, List[Location]]:
    """대화 히스토리를 포함해 OpenAI에 질의하고 (답변 텍스트, 매칭된 장소 목록)을 반환합니다.

    지도 연동용 locations는 사용자 질문이 아니라 **LLM이 실제로 답변에서 언급/추천한
    장소**를 기준으로 매칭합니다(사용자 질문 매칭은 프롬프트 컨텍스트 조립에만 사용).

    OpenAI 호출 실패/타임아웃 시 예외를 그대로 전파하며, 라우터가 502로 변환합니다.
    """
    if not settings.OPENAI_API_KEY:
        return DEMO_REPLY, find_matching_locations(db, message)

    system_prompt = SYSTEM_PROMPT
    context = build_context(find_matching_locations(db, message))
    if context:
        system_prompt = f"{SYSTEM_PROMPT}\n\n[참고 데이터]\n{context}"

    # 비용 제약(명세 §7)에 따라 최근 N턴(user+assistant 쌍)만 전송
    recent_history = history[-(settings.CHAT_HISTORY_TURNS * 2):]

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in recent_history]
    messages.append({"role": "user", "content": message})

    client = openai.OpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.OPENAI_TIMEOUT,
    )
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
    )
    reply = response.choices[0].message.content

    # LLM 답변 텍스트에서 실제로 언급된 장소를 매칭해 지도 이동/검색 트리거로 사용
    locations = find_matching_locations(db, reply)
    return reply, locations
