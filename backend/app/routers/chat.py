import traceback

import openai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services import chat as chat_service


router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat_with_ai(chat_req: ChatRequest, db: Session = Depends(get_db)):
    try:
        reply = chat_service.generate_reply(
            db,
            chat_req.message,
            chat_req.history,
        )
    except openai.OpenAIError:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail="AI 응답 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        )

    return ChatResponse(reply=reply)
