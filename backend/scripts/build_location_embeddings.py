"""locations 테이블을 임베딩해 챗봇의 취향 기반 장소 추천(RAG)용 벡터 인덱스를 생성합니다.

seed.py로 DB를 채운 뒤 1회 실행하면 backend/data/location_embeddings.npz 파일이 생성되고,
app/services/chat.py가 이 파일을 로드해 코사인 유사도 검색에 사용합니다.
(embedding 모델/차원 상수는 app/services/chat.py와 반드시 동일해야 하므로 그쪽 값을 그대로 가져다 씁니다.)

사용법: cd backend && python scripts/build_location_embeddings.py
"""
import os
import sys

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai

from app.core.config import settings
from app.database import SessionLocal
from app.models.location import Location
from app.services.chat import EMBEDDING_DIM, EMBEDDING_MODEL, LOCATION_EMBEDDINGS_PATH, location_embedding_text

BATCH_SIZE = 200


def main():
    if not settings.OPENAI_API_KEY:
        print("[Error] OPENAI_API_KEY가 설정되어 있지 않습니다. backend/.env를 확인하세요.")
        return

    db = SessionLocal()
    locations = db.query(Location).order_by(Location.id).all()
    db.close()

    if not locations:
        print("[Warn] locations 테이블이 비어 있습니다. scripts/seed.py를 먼저 실행하세요.")
        return

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT)

    ids = []
    vectors = []

    for i in range(0, len(locations), BATCH_SIZE):
        batch = locations[i:i + BATCH_SIZE]
        texts = [location_embedding_text(loc) or loc.name for loc in batch]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts, dimensions=EMBEDDING_DIM)
        for loc, item in zip(batch, response.data):
            ids.append(loc.id)
            vectors.append(item.embedding)
        print(f"[{min(i + BATCH_SIZE, len(locations))}/{len(locations)}] 임베딩 생성 완료")

    ids_arr = np.array(ids, dtype=np.int64)
    vectors_arr = np.array(vectors, dtype=np.float32)

    # 코사인 유사도를 런타임에서 내적(dot product)만으로 계산할 수 있도록 단위 벡터로 정규화
    norms = np.linalg.norm(vectors_arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors_arr = vectors_arr / norms

    os.makedirs(os.path.dirname(LOCATION_EMBEDDINGS_PATH), exist_ok=True)
    np.savez_compressed(LOCATION_EMBEDDINGS_PATH, ids=ids_arr, vectors=vectors_arr)
    print(f"저장 완료: {LOCATION_EMBEDDINGS_PATH} ({len(ids)}개 장소, {EMBEDDING_DIM}차원)")


if __name__ == "__main__":
    main()
