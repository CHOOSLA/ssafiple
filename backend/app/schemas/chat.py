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

class ChatResponse(BaseModel):
    reply: str


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
