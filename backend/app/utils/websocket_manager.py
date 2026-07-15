"""장소별 실시간 익명 채팅(FR-CHT §5.4) Pub/Sub 커넥션 매니저.

인증이 없으므로 접속 시 닉네임을 발급하고, 장소(location_id)별 방에
연결된 모든 소켓에 메시지를 broadcast하는 역할만 담당합니다.
"""
from typing import Dict, List

from fastapi import WebSocket

from app.services.chat_service import generate_nickname


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: Dict[str, List[WebSocket]] = {}
        self._nicknames: Dict[WebSocket, str] = {}

    async def connect(self, location_id: str, websocket: WebSocket) -> str:
        await websocket.accept()
        nickname = generate_nickname()
        self._rooms.setdefault(location_id, []).append(websocket)
        self._nicknames[websocket] = nickname
        return nickname

    def disconnect(self, location_id: str, websocket: WebSocket) -> str:
        nickname = self._nicknames.pop(websocket, "익명")
        room = self._rooms.get(location_id, [])
        if websocket in room:
            room.remove(websocket)
        if not room and location_id in self._rooms:
            del self._rooms[location_id]
        return nickname

    async def broadcast(self, location_id: str, payload: dict) -> None:
        for websocket in list(self._rooms.get(location_id, [])):
            try:
                await websocket.send_json(payload)
            except Exception:
                # 끊긴 소켓으로의 전송 실패는 다음 disconnect 처리에서 정리되므로 무시
                continue


manager = ConnectionManager()
