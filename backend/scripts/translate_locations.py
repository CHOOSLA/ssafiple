"""장소(locations) 명칭·주소 영문 배치 번역 스크립트 (§C-1).

- 미번역(name_en 또는 address_en이 NULL) 행만 처리하므로 재실행 시 멱등하다.
- 20건을 한 번의 OpenAI 호출로 묶고(JSON 배열), 스레드 8개로 병렬 요청해
  6,000여 건 기준 수 분 내에 완료된다. (건당 1호출 순차 방식은 4시간 이상 소요)
- OpenAI 호출은 스레드에서, SQLite 쓰기는 메인 스레드에서만 수행한다
  (SQLite 단일 쓰기 제약).
"""
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

# 상위 폴더(backend)를 sys.path에 추가하여 app 모듈을 임포트할 수 있도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.database import SessionLocal
from app.models.location import Location

CHUNK_SIZE = 20
MAX_WORKERS = 8

SYSTEM_PROMPT = (
    "You are a professional translator. Translate each Korean place name and address into English. "
    'Return ONLY a JSON object of the form {"items": [{"id": <id>, "name_en": "...", "address_en": "..."}, ...]} '
    "with exactly one entry per input item, keeping the same ids. "
    "Romanize proper nouns using the standard Revised Romanization of Korean."
)


def translate_chunk(client, chunk):
    """chunk: [(id, name, address)] → {id: (name_en, address_en)}"""
    payload = [{"id": i, "name": n, "address": a or ""} for i, n, a in chunk]
    response = client.chat.completions.create(
        model=settings.OPENAI_TRANSLATE_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )
    items = json.loads(response.choices[0].message.content).get("items", [])
    return {int(it["id"]): (it.get("name_en"), it.get("address_en")) for it in items if "id" in it}


def main():
    # OpenAI()는 os.environ만 읽고 backend/.env는 자동 로드되지 않으므로 settings에서 주입
    if not settings.OPENAI_API_KEY:
        print("OPENAI_API_KEY가 설정되지 않았습니다. backend/.env를 확인하세요.")
        return
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    db = SessionLocal()
    try:
        rows = (
            db.query(Location.id, Location.name, Location.address)
            .filter((Location.name_en == None) | (Location.address_en == None))  # noqa: E711
            .all()
        )
        if not rows:
            print("모든 장소가 이미 번역되어 있습니다.")
            return

        total = len(rows)
        print(f"미번역 {total}건 — {CHUNK_SIZE}건 단위 / 스레드 {MAX_WORKERS}개로 번역 시작", flush=True)

        chunks = [rows[i:i + CHUNK_SIZE] for i in range(0, total, CHUNK_SIZE)]
        done = 0
        failed_chunks = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(translate_chunk, client, chunk): chunk for chunk in chunks}
            for future in as_completed(futures):
                chunk = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    failed_chunks += 1
                    print(f" -> 청크 실패 ({chunk[0][0]}~): {e}", flush=True)
                    continue

                # SQLite 쓰기는 메인 스레드에서만
                for loc_id, (name_en, address_en) in result.items():
                    db.query(Location).filter(Location.id == loc_id).update(
                        {"name_en": name_en, "address_en": address_en}
                    )
                db.commit()
                done += len(result)
                if done % 200 < CHUNK_SIZE:
                    print(f" 진행: {done}/{total}", flush=True)

        print(f"완료: {done}/{total} (실패 청크 {failed_chunks}개 — 재실행하면 실패분만 다시 처리)", flush=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
