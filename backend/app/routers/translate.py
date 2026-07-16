import traceback

import openai
from fastapi import APIRouter, HTTPException

from app.schemas import TranslateRequest, TranslateResponse
from app.services import translation as translation_service

router = APIRouter(prefix="/translate", tags=["translate"])


@router.post("", response_model=TranslateResponse)
def translate_text(req: TranslateRequest):
    # DB 세션 주입 없음 — 서비스가 캐시 조회/저장 시에만 짧게 세션을 연다
    # (OpenAI 대기 중 커넥션 점유로 인한 QueuePool 고갈 방지)
    try:
        translated = translation_service.translate(req.text, req.target_lang)
    except openai.OpenAIError:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail="번역에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        )
    return TranslateResponse(translated=translated)
