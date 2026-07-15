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
    "관광": "관광지", "명소": "관광지", "구경": "관광지",
    "전시": "문화시설", "박물관": "문화시설", "문화": "문화시설", "공연": "문화시설",
    "쇼핑": "쇼핑", "백화점": "쇼핑",
    "숙박": "숙박", "호텔": "숙박", "게스트하우스": "숙박",
}

SYSTEM_PROMPT = (
    "당신은 서울 여행 정보 커뮤니티 'SSAFIPLE'의 AI 여행 비서입니다. "
    "이 서비스가 다루는 장소 카테고리는 관광지, 문화시설, 숙박, 쇼핑, 레포츠, 축제/공연, 여행코스 7가지뿐이며 "
    "음식점/맛집/카페 데이터는 보유하고 있지 않으니 관련 질문에는 지원하지 않는다고 솔직히 안내하세요. "
    "위 7개 카테고리 범위 내에서 한국어로 친절하고 간결하게 답변하세요. "
    "답변은 3~5문장 이내로 요약하고, 확실하지 않은 정보는 추측하지 말고 모른다고 밝히세요. "
    "서울 여행 안내와 무관한 질문에는 정중히 답변할 수 없다고 안내하세요. "
    "볼드(**...**) 표기는 지도 이동에 직접 쓰이는 매우 중요한 신호이므로 아래 규칙을 엄격히 지키세요: "
    "1) [참고 데이터]에 실제로 존재하고 사용자에게 방문을 권하는 구체적인 가게/장소 고유명사에만 볼드를 사용하세요. "
    "2) 지하철역명·동네/지역명(예: 건대입구, 홍대), 음식 종류나 메뉴(예: 샤브샤브, 국밥), "
    "비교·제외·예시로만 언급한 장소는 절대 볼드로 표시하지 마세요. "
    "3) [참고 데이터]에 질문과 맞는 장소가 없다면 볼드를 하나도 쓰지 말고, "
    "구체적으로 추천할 데이터가 없다고 솔직히 답하세요. "
    "4) [참고 데이터]에 실제로 존재하는지 확인되지 않은 가게 이름은 절대 지어내지 마세요. "
    "그럴듯하게 들리는 이름이라도 [참고 데이터]에 없으면 언급도, 볼드 표시도 하지 마세요."
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
    2) 이름 매칭이 하나도 없으면 카테고리 힌트 키워드(관광→관광지 등)로 보조 매칭.
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
    """LLM 답변에서 실제로 추천된 장소를 찾아 지도 연동용으로 반환합니다.

    답변의 **볼드** 강조 구문만 후보로 사용합니다(SYSTEM_PROMPT가 실제 추천 장소에만
    볼드를 쓰고, 역명/동네명/음식종류/비교 대상에는 쓰지 말라고 엄격히 지시함).

    의도적으로 전체 텍스트 키워드 매칭으로 폴백하지 않습니다: 일반 서술 문장에는 "건대입구",
    "인근"처럼 흔하지만 장소명은 아닌 단어가 자주 등장하고, 이런 단어가 "OO건대입구점" 같은
    무관한 프랜차이즈 매장명과 우연히 겹쳐 매칭되는 문제가 있었습니다. 볼드 강조가 없다면
    "추천할 장소를 확신할 수 없다"는 신호로 보고 지도 연동 없이 빈 목록을 반환합니다.
    """
    matched: dict[int, Location] = {}

    for phrase in _extract_bold_phrases(reply_text):
        if len(matched) >= limit:
            break
        if len(phrase) < 3:
            # 2글자 이하 볼드 구문은 무관한 상호명과 우연히 겹칠 위험이 커서 매칭을 시도하지 않음
            # (예: LLM이 지어낸 "거안"이 "타이거안경원"에 우연히 포함되는 경우)
            continue
        rows = db.query(Location).filter(Location.name.like(f"%{phrase}%")).limit(limit).all()
        if not rows:
            for token in _extract_tokens(phrase):
                rows = db.query(Location).filter(Location.name.like(f"%{token}%")).limit(limit).all()
                if rows:
                    break
        for loc in rows:
            matched.setdefault(loc.id, loc)

    return list(matched.values())[:limit]


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
    db: Session, message: str, history: List[ChatMessage]
) -> Tuple[str, List[Location]]:
    """대화 히스토리를 포함해 OpenAI에 질의하고 (답변 텍스트, 매칭된 장소 목록)을 반환합니다.

    사용자는 버튼으로 취향/기분을 선택하지 않고 처음부터 자유 텍스트로 대화합니다.
    질의 메시지를 임베딩해 사전 계산된 장소 임베딩과 코사인 유사도로 후보를 검색하고,
    이를 RAG 컨텍스트로 주입해 LLM이 실제 DB 장소를 추천하도록 유도합니다.

    지도 연동용 locations는 사용자 질문이 아니라 **LLM이 실제로 답변에서 언급/추천한
    장소**를 기준으로 매칭합니다.

    OpenAI 호출 실패/타임아웃 시 예외를 그대로 전파하며, 라우터가 502로 변환합니다.
    """
    query_text = message

    if not settings.OPENAI_API_KEY:
        return DEMO_REPLY, find_matching_locations(db, query_text)

    # 대화가 처음이든 이어지는 중이든, 사용자의 요청이 막연하면(지역/카테고리/분위기 중
    # 뭔가 빠져 있으면) 장소를 바로 나열하지 말고 부족한 정보를 되물어보게 유도한다.
    system_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "사용자의 요청에 지역, 장소 카테고리(관광지/문화시설/숙박/쇼핑/레포츠/축제·공연/여행코스), "
        "원하는 분위기 중 무언가가 빠져 있어 막연하다면(예: \"어디 가지?\", \"추천해줘\") "
        "장소를 바로 나열하지 말고, 부족한 정보를 한 문장으로 짧게 되물어보세요. "
        "요청에 이미 구체적인 지역/카테고리/분위기가 충분히 담겨 있다면 바로 추천해도 됩니다."
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
