import traceback

import openai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TranslateRequest, TranslateResponse
from app.services import translation as translation_service

router = APIRouter(prefix="/translate", tags=["translate"])


@router.post("", response_model=TranslateResponse)
def translate_text(req: TranslateRequest, db: Session = Depends(get_db)):
    try:
        translated = translation_service.translate(db, req.text, req.target_lang)
    except openai.OpenAIError:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail="번역에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        )
    return TranslateResponse(translated=translated)
