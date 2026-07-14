from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.core.config import settings
import openai

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
def chat_with_ai(chat_req: ChatRequest, db: Session = Depends(get_db)):
    """
    AI 챗봇 서비스 엔드포인트
    비용 제약 및 성능 확보를 위해 DB(관광지 및 게시판) 정보를 우선 조회한 후 컨텍스트를 OpenAI로 전달합니다.
    """
    if not settings.OPENAI_API_KEY:
        # API Key가 없는 상태에서는 사용자 메시지를 메아리해주는 데모 모드로 동작하도록 안전장치 구성
        return ChatResponse(
            reply=f"[LocalHub AI - 데모 모드] 현재 OpenAI API Key가 구성되지 않았습니다.\n"
                  f"전송된 질문: '{chat_req.message}'\n"
                  f"(.env 파일에 OPENAI_API_KEY를 입력해 주세요.)"
        )

    try:
        # OpenAI 최신 SDK(v1.0.0+) 연동 규격 준수
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # TODO: 명세 CHT-01 로직에 따라 DB 사전 검색 결과(관광지/게시글)를 바탕으로 Prompt 조립
        # (상세 로직은 backend/app/services/chat.py 서비스 계층에서 추후 구체화)
        
        system_prompt = (
            "당신은 서울시 공식 관광 안내 챗봇 비서 'LocalHub AI'입니다. "
            "사용자의 질문에 친절하고 정중하게 서울 사투리나 서울의 지역 문화를 섞어 한국어로 대답하세요. "
            "주어진 서울 관광지 정보(locations)와 유저 후기 게시판(posts) 데이터를 컨텍스트로 삼아 정확하고 근거 있는 정보를 추천해야 합니다."
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_req.message}
            ]
        )
        
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI 챗봇 연동 도중 에러가 발생했습니다: {str(e)}")
