from typing import Literal
from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    """UGC 온디맨드 번역 요청(§C-2). text는 최대 2,000자, 초과 시 422."""
    text: str = Field(min_length=1, max_length=2000)
    target_lang: Literal["en", "ko"]


class TranslateResponse(BaseModel):
    translated: str
