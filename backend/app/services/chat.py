"""AI 챗봇(FR-CHT-01) 서비스 계층.

라우터는 HTTP 관심사(요청 검증, 상태 코드)만 담당하고,
프롬프트 조립 및 OpenAI 호출은 모두 이 모듈에서 처리합니다.
"""
import os
import re
from typing import List, Optional, Tuple

import numpy as np
import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Location
from app.schemas import ChatMessage

# 챗봇 답변에서 지도 이동/검색 연동에 사용할 장소 매칭 최대 개수
MAX_MATCHED_LOCATIONS = 3

# 취향 기반 장소 추천(RAG 컨텍스트)에 사용할 임베딩 검색 설정.
# scripts/build_location_embeddings.py가 동일한 모델/차원으로 인덱스를 생성해야 함.
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 256
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCATION_EMBEDDINGS_PATH = os.path.join(_BACKEND_DIR, "data", "location_embeddings.npz")
RETRIEVAL_TOP_K = 5

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
    "서울 여행 안내와 무관한 질문에는 정중히 답변할 수 없다고 안내하세요. "
    "본문에서 언급하는 구체적 장소명은 예외 없이 **장소명**처럼 마크다운 볼드로 표시하세요"
    "(지도 연동에 쓰이는 중요한 규칙이니 장소를 나열/비교/제안하는 모든 경우에 지키세요)."
)

DEMO_REPLY = (
    "[데모 모드] 현재 OpenAI API Key가 설정되지 않아 실제 답변을 생성할 수 없습니다.\n"
    "backend/.env 파일에 OPENAI_API_KEY를 입력한 뒤 서버를 다시 시작해 주세요."
)


def _extract_tokens(message: str) -> List[str]:
    """메시지에서 장소명 매칭 후보가 될 3글자 이상 단어를 추출합니다.

    2글자로는 "사람", "장소"처럼 무관한 장소명과 우연히 겹치는 흔한 단어가 많이 걸려
    최소 길이를 3으로 둔다(예: "안경과 사람들"이 "사람"에 우연히 매칭되는 문제 방지).
    """
    words = re.findall(r"[가-힣A-Za-z0-9]{3,}", message)
    return [w for w in words if w not in _STOPWORDS]


def _extract_bold_phrases(text: str) -> List[str]:
    """마크다운 **볼드** 표기를 LLM이 강조한 장소명 후보로 간주해 추출합니다."""
    return [p.strip() for p in re.findall(r"\*\*(.+?)\*\*", text) if p.strip()]


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


def find_mentioned_locations(db: Session, reply_text: str, limit: int = MAX_MATCHED_LOCATIONS) -> List[Location]:
    """LLM 답변에서 실제로 추천/언급된 장소를 찾아 지도 연동용으로 반환합니다.

    답변의 **볼드** 강조 구문(SYSTEM_PROMPT가 장소명에 볼드를 쓰도록 지시함)을 우선 후보로
    사용합니다. 볼드 구문 단위로만 토큰을 추출하므로, 강조되지 않은 일반 서술 문장에 등장하는
    흔한 단어(예: "사람")가 무관한 장소명과 우연히 겹쳐 매칭되는 것을 방지합니다.
    볼드 강조가 없거나 매칭 결과가 없으면 전체 텍스트 키워드 매칭(find_matching_locations)으로
    폴백합니다.
    """
    matched: dict[int, Location] = {}

    for phrase in _extract_bold_phrases(reply_text):
        if len(matched) >= limit:
            break
        rows = db.query(Location).filter(Location.name.like(f"%{phrase}%")).limit(limit).all()
        if not rows:
            for token in _extract_tokens(phrase):
                rows = db.query(Location).filter(Location.name.like(f"%{token}%")).limit(limit).all()
                if rows:
                    break
        for loc in rows:
            matched.setdefault(loc.id, loc)

    if matched:
        return list(matched.values())[:limit]

    return find_matching_locations(db, reply_text, limit)


def location_embedding_text(loc: Location) -> str:
    """장소 임베딩 생성에 쓰일 텍스트 표현. build_location_embeddings.py와 반드시 동일 로직 사용."""
    parts = [loc.name, loc.category, loc.address, loc.description]
    return " ".join(p for p in parts if p)[:500]


# 임베딩 인덱스 캐시: None=아직 미로드, False=파일 없음(폴백), (ids, vectors)=로드 완료
_embedding_index_cache: Optional[object] = None


def _load_location_embeddings():
    global _embedding_index_cache
    if _embedding_index_cache is None:
        if os.path.exists(LOCATION_EMBEDDINGS_PATH):
            data = np.load(LOCATION_EMBEDDINGS_PATH)
            _embedding_index_cache = (data["ids"], data["vectors"])
        else:
            _embedding_index_cache = False
    return _embedding_index_cache or None


def retrieve_candidate_locations(db: Session, query_text: str, limit: int = RETRIEVAL_TOP_K) -> List[Location]:
    """질의 텍스트(사용자 메시지+취향)를 임베딩해 사전 계산된 장소 임베딩과 코사인 유사도로
    후보 장소를 검색합니다. 이 후보는 LLM 프롬프트의 컨텍스트로만 쓰이며, 실제 지도 연동용
    locations는 generate_reply()에서 LLM 응답 텍스트를 별도로 매칭해 결정합니다.

    임베딩 인덱스 파일(scripts/build_location_embeddings.py 미실행)이 없거나 API 키가 없으면
    기존 키워드 매칭(find_matching_locations)으로 폴백합니다.
    """
    cached = _load_location_embeddings()
    if cached is None or not settings.OPENAI_API_KEY:
        return find_matching_locations(db, query_text, limit)

    ids, vectors = cached
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT)
    try:
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=query_text, dimensions=EMBEDDING_DIM)
    except openai.OpenAIError:
        return find_matching_locations(db, query_text, limit)

    query_vec = np.array(response.data[0].embedding, dtype=np.float32)
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm

    similarities = vectors @ query_vec
    top_indices = np.argsort(-similarities)[:limit]
    top_ids = [int(ids[i]) for i in top_indices]

    rows = db.query(Location).filter(Location.id.in_(top_ids)).all()
    rows_by_id = {row.id: row for row in rows}
    return [rows_by_id[i] for i in top_ids if i in rows_by_id]


def build_context(locations: List[Location]) -> str:
    """매칭된 장소 목록을 OpenAI 시스템 프롬프트에 주입할 컨텍스트 문자열로 조립합니다."""
    if not locations:
        return ""
    lines = [
        f"- {loc.name} ({loc.category or '기타'}): {loc.address or '주소 정보 없음'}"
        for loc in locations
    ]
    return "\n".join(lines)


def generate_reply(
    db: Session, message: str, history: List[ChatMessage], preferences: str = ""
) -> Tuple[str, List[Location]]:
    """대화 히스토리를 포함해 OpenAI에 질의하고 (답변 텍스트, 매칭된 장소 목록)을 반환합니다.

    preferences는 매 요청마다 사용자가 그때그때 입력하는 취향 힌트(예: "조용한 자연 위주",
    "매운 음식 좋아함")로, 서버에 영속 저장하지 않고 요청 컨텍스트에만 사용합니다.
    질의(메시지+취향)를 임베딩해 사전 계산된 장소 임베딩과 코사인 유사도로 후보를 검색하고,
    이를 RAG 컨텍스트로 주입해 LLM이 취향에 맞는 실제 DB 장소를 추천하도록 유도합니다.

    지도 연동용 locations는 사용자 질문이 아니라 **LLM이 실제로 답변에서 언급/추천한
    장소**를 기준으로 매칭합니다(취향 기반 검색은 프롬프트 컨텍스트 조립에만 사용).

    OpenAI 호출 실패/타임아웃 시 예외를 그대로 전파하며, 라우터가 502로 변환합니다.
    """
    query_text = f"{message} (선호 취향: {preferences})" if preferences else message

    if not settings.OPENAI_API_KEY:
        return DEMO_REPLY, find_matching_locations(db, query_text)

    system_prompt = SYSTEM_PROMPT
    if preferences:
        system_prompt = f"{system_prompt}\n\n사용자가 밝힌 취향/선호: {preferences}. 가능하면 이 취향에 맞는 장소를 우선 추천하세요."
    elif not history:
        # 취향 미선택 + 첫 대화: 막연한 질문이면 장소를 바로 나열하지 말고 취향/기분을 되물어보게 유도
        system_prompt = (
            f"{system_prompt}\n\n"
            "사용자가 아직 취향을 밝히지 않았고 이번이 첫 대화입니다. "
            "질문이 막연하다면(예: \"어디 가지?\", \"추천해줘\") 장소를 바로 나열하지 말고, "
            "어떤 분위기나 취향을 원하는지 한 문장으로 짧게 되물어보세요. "
            "질문에 이미 구체적인 지역/카테고리가 담겨 있다면 바로 추천해도 됩니다."
        )

    context = build_context(retrieve_candidate_locations(db, query_text))
    if context:
        system_prompt = f"{system_prompt}\n\n[참고 데이터]\n{context}"

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
    locations = find_mentioned_locations(db, reply)
    return reply, locations
