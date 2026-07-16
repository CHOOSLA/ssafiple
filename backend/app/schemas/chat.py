import datetime
from typing import List, Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """대화 히스토리 1건. OpenAI Chat Completions 규격과 동일한 role/content 형태를 사용합니다."""
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    # 빈 메시지는 422로 거절 (명세 FR-CHT-01 예외 처리)
    message: str = Field(min_length=1, max_length=500)
    history: List[ChatMessage] = []
    # 응답 언어 (프론트 로케일). 장소 데이터·검색은 한국어 기준이지만 답변 언어만 전환
    lang: Literal["ko", "en"] = "ko"

class LocationBrief(BaseModel):
    """챗봇이 답변과 함께 추천하는 장소의 지도 연동용 요약 정보."""
    id: int
    name: str
    category: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    reply: str
    locations: List[LocationBrief] = []


class ChatWsIncoming(BaseModel):
    """장소별 실시간 채팅(FR-CHT §5.4) WebSocket 수신 메시지 규격."""
    content: str = Field(min_length=1, max_length=300)


class ChatMessageOut(BaseModel):
    id: int
    nickname: str
    content: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
