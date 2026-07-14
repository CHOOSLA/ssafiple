import os
import json
import sys

# backend/ 경로를 sys.path에 추가하여 app 패키지를 가져올 수 있도록 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.location import Location

def load_json_files(raw_dir):
    """
    data/raw/ 디렉토리 내 모든 .json 파일을 읽어 관광지 리스트를 반환합니다.
    """
    locations = []
    if not os.path.exists(raw_dir):
        print(f"[Warn] Raw data directory not found at: {raw_dir}")
        return locations

    for filename in os.listdir(raw_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(raw_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 만약 루트가 리스트가 아니라 특정 키(예: 'records')를 가진 객체라면 이에 대응해야 함
                    items = data if isinstance(data, list) else data.get("records", [])
                    
                    # 파일 이름 등에서 카테고리 추출 유추 가능 (예: '서울_관광지.json' -> '관광지')
                    category_fallback = filename.replace("서울_", "").replace(".json", "")
                    
                    for item in items:
                        # JSON 키 매핑은 데이터 포맷에 맞게 조정이 필요합니다.
                        # 명세서 2.1에 따른 mapx(경도), mapy(위도) 키 획득
                        name = item.get("name") or item.get("title") or item.get("명칭")
                        address = item.get("address") or item.get("addr") or item.get("주소")
                        category = item.get("category") or item.get("종류") or category_fallback
                        description = item.get("description") or item.get("content") or item.get("개요")
                        
                        # 지도 좌표 (mapx, mapy) 또는 (lon, lat) 추출
                        longitude_raw = item.get("mapx") or item.get("lon") or item.get("경도")
                        latitude_raw = item.get("mapy") or item.get("lat") or item.get("위도")
                        
                        if name and longitude_raw and latitude_raw:
                            try:
                                longitude = float(longitude_raw)
                                latitude = float(latitude_raw)
                                
                                # ⚠️ [코드 리뷰 체크 대비 자동 불변식 검증] (경도/위도 뒤바뀜 방지)
                                # 서울시 Bounding Box 범위 체크 검증
                                assert 126.75 <= longitude <= 127.20, f"경도(longitude)가 서울 범위를 벗어남: {longitude} (관광지: {name})"
                                assert 37.40 <= latitude <= 37.72, f"위도(latitude)가 서울 범위를 벗어남: {latitude} (관광지: {name})"
                                
                                locations.append({
                                    "name": name.strip(),
                                    "category": category.strip(),
                                    "address": address.strip() if address else None,
                                    "latitude": latitude,
                                    "longitude": longitude,
                                    "description": description.strip() if description else None
                                })
                            except (ValueError, AssertionError) as e:
                                print(f"[Error] Validation failed for target '{name}': {e}")
                                continue
            except Exception as e:
                print(f"[Error] Failed to read file {filename}: {e}")
    return locations

def seed_data():
    db = SessionLocal()
    
    # 1. 테이블 스키마 보장
    Base.metadata.create_all(bind=engine)
    
    # 2. Raw 데이터 경로 지정
    # project_root/data/raw/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_data_dir = os.path.join(project_root, "data", "raw")
    
    print("Starting database seeding...")
    locations_to_seed = load_json_files(raw_data_dir)
    
    if not locations_to_seed:
        print("No valid locations found to seed. Please place your JSON files under data/raw/.")
        db.close()
        return

    # 3. 데이터 중복 체크 및 적재
    inserted_count = 0
    for loc_data in locations_to_seed:
        # 중복 방지 (관광지 이름 기준)
        existing = db.query(Location).filter(Location.name == loc_data["name"]).first()
        if not existing:
            new_loc = Location(**loc_data)
            db.add(new_loc)
            inserted_count += 1
            
    db.commit()
    print(f"Successfully seeded {inserted_count} new locations into localhub.db!")
    db.close()

if __name__ == "__main__":
    seed_data()
