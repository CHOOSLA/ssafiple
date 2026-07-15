import traceback
from typing import List

import openai
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
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
            chat_req.preferences,
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


@router.websocket("/ws/{location_id}")
async def chat_room(websocket: WebSocket, location_id: str, db: Session = Depends(get_db)):
    db_loc = db.query(Location).filter(Location.id == location_id).first()
    if not db_loc:
        await websocket.close(code=4404)
        return

    nickname = await manager.connect(location_id, websocket)
    await websocket.send_json({"type": "self", "nickname": nickname})
    await manager.broadcast(location_id, {
        "type": "system",
        "content": f"{nickname}님이 입장했습니다.",
    })

    try:
        while True:
            raw = await websocket.receive_json()
            try:
                incoming = ChatWsIncoming.model_validate(raw)
            except ValidationError:
                continue

            message = place_chat_service.save_message(db, location_id, nickname, incoming.content)
            await manager.broadcast(location_id, {
                "type": "message",
                "nickname": message.nickname,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            })
    except WebSocketDisconnect:
        manager.disconnect(location_id, websocket)
        await manager.broadcast(location_id, {
            "type": "system",
            "content": f"{nickname}님이 퇴장했습니다.",
        })
