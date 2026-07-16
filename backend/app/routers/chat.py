import traceback
from typing import List

import openai
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import SessionLocal, get_db
from app.models import Location
from app.schemas import ChatRequest, ChatResponse, ChatMessageOut, ChatWsIncoming
from app.services import chat as chat_service
from app.services import chat_service as place_chat_service
from app.utils.websocket_manager import manager


router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat_with_ai(chat_req: ChatRequest, db: Session = Depends(get_db)):
    try:
        reply, locations = chat_service.generate_reply(
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

    return ChatResponse(reply=reply, locations=locations)


@router.get("/rooms/{location_id}/messages", response_model=List[ChatMessageOut])
def get_room_messages(location_id: str, db: Session = Depends(get_db)):
    db_loc = db.query(Location).filter(Location.id == location_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="관광지 정보를 찾을 수 없습니다.")
    return place_chat_service.get_recent_messages(db, location_id)


# WebSocket 핸들러는 소켓 수명 내내 살아있으므로 Depends(get_db)로 세션을 받으면
# 접속자 1명이 커넥션 풀 1개를 접속 종료까지 점유해 풀이 고갈됨(QueuePool limit reached).
# DB가 필요한 순간에만 아래 헬퍼로 세션을 짧게 열고 즉시 반납한다.
def _location_exists(location_id: str) -> bool:
    with SessionLocal() as db:
        return db.query(Location).filter(Location.id == location_id).first() is not None


def _save_message(location_id: str, nickname: str, content: str):
    with SessionLocal() as db:
        return place_chat_service.save_message(db, location_id, nickname, content)


@router.websocket("/ws/{location_id}")
async def chat_room(websocket: WebSocket, location_id: str):
    # 동기 DB 호출은 threadpool로 위임해 이벤트 루프 블로킹을 방지
    exists = await run_in_threadpool(_location_exists, location_id)
    if not exists:
        await websocket.close(code=4404)
        return

    nickname = await manager.connect(location_id, websocket)
    await websocket.send_json({"type": "self", "nickname": nickname})
    await manager.broadcast(location_id, {
        "type": "system",
        "event": "join",
        "nickname": nickname,
    })

    try:
        while True:
            raw = await websocket.receive_json()
            try:
                incoming = ChatWsIncoming.model_validate(raw)
            except ValidationError:
                continue

            message = await run_in_threadpool(
                _save_message, location_id, nickname, incoming.content
            )
            await manager.broadcast(location_id, {
                "type": "message",
                "nickname": message.nickname,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            })
    except WebSocketDisconnect:
        pass
    finally:
        # WebSocketDisconnect 외의 예외로 루프를 벗어나도 방에서 소켓을 정리
        manager.disconnect(location_id, websocket)
        await manager.broadcast(location_id, {
            "type": "system",
            "event": "leave",
            "nickname": nickname,
        })
