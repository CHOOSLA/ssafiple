"""AI 챗봇(FR-CHT-01) 서비스 계층.

라우터는 HTTP 관심사(요청 검증, 상태 코드)만 담당하고,
프롬프트 조립 및 OpenAI 호출은 모두 이 모듈에서 처리합니다.
"""
from typing import List

import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas import ChatMessage

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


def build_context(db: Session, message: str) -> str:
    """사용자 질의와 관련된 DB(locations, posts) 검색 결과를 컨텍스트 문자열로 조립합니다.

    ⚠️ 미구현(CHT-01 RAG). 현재 locations/posts 테이블이 비어 있어 검색 대상이 없으므로
    빈 문자열을 반환합니다. data/raw/ 시드 데이터가 적재된 뒤 이 함수만 채우면
    generate_reply() 수정 없이 컨텍스트 주입이 활성화됩니다.
    """
    return ""


def generate_reply(db: Session, message: str, history: List[ChatMessage]) -> str:
    """대화 히스토리를 포함해 OpenAI에 질의하고 답변 텍스트를 반환합니다.

    OpenAI 호출 실패/타임아웃 시 예외를 그대로 전파하며, 라우터가 502로 변환합니다.
    """
    if not settings.OPENAI_API_KEY:
        return DEMO_REPLY

    system_prompt = SYSTEM_PROMPT
    context = build_context(db, message)
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
    return response.choices[0].message.content
