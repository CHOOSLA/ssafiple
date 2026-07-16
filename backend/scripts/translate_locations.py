import os
import sys
import json
from openai import OpenAI

# 상위 폴더(backend)를 sys.path에 추가하여 app 모듈을 임포트할 수 있도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.database import SessionLocal
from app.models.location import Location

def main():
    # OpenAI()는 os.environ만 읽고 backend/.env는 자동 로드되지 않으므로 settings에서 주입
    if not settings.OPENAI_API_KEY:
        print("OPENAI_API_KEY가 설정되지 않았습니다. backend/.env를 확인하세요.")
        return
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    db = SessionLocal()
    try:
        # 이미 번역된 행은 제외 (멱등성 보장)
        untranslated = db.query(Location).filter(
            (Location.name_en == None) | (Location.address_en == None)
        ).all()
        
        if not untranslated:
            print("모든 관광지가 이미 번역되어 있습니다.")
            return

        for loc in untranslated:
            print(f"번역 중: {loc.name} / {loc.address}")
            try:
                response = client.chat.completions.create(
                    model=settings.OPENAI_TRANSLATE_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate the given Korean place name and address into English. Return ONLY JSON format: {\"name_en\": \"...\", \"address_en\": \"...\"}"},
                        {"role": "user", "content": f"Name: {loc.name}\nAddress: {loc.address}"}
                    ],
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                loc.name_en = result.get("name_en")
                loc.address_en = result.get("address_en")
                
                db.commit()
                print(f" -> 성공: {loc.name_en} / {loc.address_en}")
            except Exception as e:
                print(f" -> 실패 ({loc.id}): {e}")
                db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
