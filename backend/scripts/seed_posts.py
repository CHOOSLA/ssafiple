"""
게시판(posts) 테스트 데이터를 대량으로 채우기 위한 시드 스크립트.

locations 테이블에 이미 적재된 장소들 중 무작위로 골라 location_id로 연결하고,
템플릿 기반으로 제목/본문을 조합해 실제 장소 이름이 들어간 그럴듯한 후기 게시글을 생성한다.

실행:
    cd backend
    python scripts/seed_posts.py            # 기본 200개 생성
    python scripts/seed_posts.py --count 50  # 개수 지정
"""
import argparse
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.location import Location
from app.models.post import Post

AUTHORS = [
    "여행가꿈나무", "서울토박이", "주말산책러", "카페투어러", "혼밥러버",
    "감성사진가", "동네탐험대", "야경덕후", "먹부림전문", "산책왕",
    "맛집헌터", "힐링여행자", "뚜벅이여행", "궁궐러버", "한강러너",
]

TITLE_TEMPLATES = [
    "{name} 다녀왔어요 후기 남깁니다",
    "{name} 가보니 생각보다 좋았어요",
    "주말에 {name} 다녀온 후기",
    "{name} 근처 맛집 아시는 분?",
    "{name} 처음 가봤는데 강추합니다",
    "{name} 야경 진짜 예뻐요",
    "{name} 데이트 코스로 어때요?",
    "{name} 사진 몇 장 공유해요",
    "{name} 주차는 어디에 하셨나요",
    "{name} 다시 가고 싶은 곳",
]

# 카테고리별로 내용이 겉돌지 않도록 장소 성격에 맞춘 3~5문장짜리 후기 템플릿.
# {name}=장소명, {district}=주소에서 뽑은 구(區) 단위 지역명
CONTENT_TEMPLATES_BY_CATEGORY = {
    "쇼핑": [
        "지난 주말에 {district}에 있는 {name}에 다녀왔어요. 매장이 여러 층에 걸쳐 넓게 자리 잡고 있어서 하루 종일 둘러봐도 다 못 볼 정도였고, 브랜드도 다양해서 이것저것 비교하면서 쇼핑하기 편했습니다. 중간에 쉴 수 있는 카페나 푸드코트도 잘 갖춰져 있어서 지치지 않고 돌아볼 수 있었어요. 다음에 옷 사러 갈 때 또 들를 것 같습니다.",
        "{name} 처음 가봤는데 {district} 쪽에서는 여기가 제일 편한 것 같아요. 층마다 컨셉이 달라서 구경하는 재미가 있고, 세일 기간에 맞춰 가니 가격도 나쁘지 않았습니다. 주차 공간도 넉넉해서 차 가지고 가기에도 부담이 없더라고요. 시간 여유 있게 잡고 가시는 걸 추천드려요.",
        "{district}에 볼일이 있어서 갔다가 {name}까지 들렀는데 생각보다 규모가 커서 놀랐어요. 원하는 물건을 못 찾으면 직원분들이 친절하게 안내해주셔서 헤매지 않고 쇼핑할 수 있었습니다. 주말이라 사람은 좀 많았지만 그만큼 활기찬 분위기라 나쁘지 않았어요.",
    ],
    "관광지": [
        "{district}에 위치한 {name}에 다녀왔습니다. 옛 정취가 잘 보존되어 있어서 걷는 내내 시간을 거슬러 올라간 느낌이었고, 곳곳에 안내판도 잘 되어 있어서 역사를 몰라도 이해하기 쉬웠어요. 사진 찍기 좋은 포인트도 많아서 계속 셔터를 눌렀습니다. 다음엔 여유롭게 시간을 두고 다시 가보고 싶어요.",
        "{name}은 소문대로 볼거리가 많은 곳이었어요. 특히 {district} 쪽에서 접근하기도 편했고, 코스가 잘 정비되어 있어서 걷기에도 무리가 없었습니다. 아이들과 함께 가도 좋을 만큼 안전하고 넓어서 나들이 삼아 다녀오기 딱 좋았어요.",
        "평일 오전에 한적하게 {name}을 둘러봤는데 사람이 적어서 여유롭게 구경할 수 있었습니다. {district} 특유의 분위기와 잘 어우러져서 산책하듯 걷기 좋았고, 중간중간 쉴 벤치도 많아서 편했어요. 계절 바뀔 때마다 또 오고 싶은 곳입니다.",
    ],
    "문화시설": [
        "{name}에서 전시를 보고 왔는데 생각보다 볼거리가 많아서 시간 가는 줄 몰랐어요. {district}에 이런 조용한 공간이 있다는 게 새삼 좋았고, 관람 동선도 깔끔하게 짜여 있어서 놓치는 전시실 없이 다 둘러볼 수 있었습니다. 다음 기획전도 기대가 됩니다.",
        "{district}에 있는 {name}을 처음 방문했는데 규모에 비해 알찬 구성이었어요. 도슨트 설명을 들으면서 관람하니 이해가 훨씬 잘 됐고, 아이 동반 가족들도 꽤 보였어요. 주말보다는 평일에 가는 걸 추천드립니다, 훨씬 여유롭게 볼 수 있어요.",
        "비 오는 날 갈 곳 찾다가 {name}에 다녀왔는데 실내라 날씨 걱정 없이 편하게 관람했습니다. {district} 근처에서 데이트 코스로도 손색없을 것 같고, 기념품 숍도 알차게 꾸며져 있어서 구경하는 재미가 쏠쏠했어요.",
    ],
    "숙박": [
        "출장 때문에 {name}에 묵었는데 위치가 {district} 중심가라 이동하기 정말 편했어요. 객실이 깔끔하고 침구도 편해서 푹 쉴 수 있었고, 직원분들도 친절하셔서 만족스러운 숙박이었습니다. 다음에 서울 올 일 있으면 또 예약할 것 같아요.",
        "{district} 여행 겸해서 {name}에서 1박 했는데 조식이 특히 좋았습니다. 방음도 잘 되어 있어서 밤에 조용히 잘 수 있었고, 체크인·체크아웃도 빠르게 처리해주셔서 스트레스 없었어요. 가성비 괜찮은 숙소를 찾으신다면 추천드려요.",
        "{name}은 {district} 근처 관광지들이랑 가까워서 동선 짜기 편했어요. 룸 컨디션도 사진이랑 비슷하게 깔끔했고, 주차도 무료로 지원돼서 차 가지고 가시는 분들도 부담 없을 것 같습니다.",
    ],
    "축제공연행사": [
        "{name} 다녀왔어요! 사람은 많았지만 그만큼 볼거리랑 즐길 거리가 풍성해서 시간 가는 줄 몰랐습니다. {district} 일대가 온통 축제 분위기로 들썩이더라고요. 먹거리 부스도 다양해서 배부르게 즐기고 왔어요.",
        "{district}에서 열린 {name}에 다녀왔는데 공연 라인업이 알차서 끝까지 자리 뜨지 않고 봤습니다. 대기 줄이 있긴 했지만 진행 요원분들이 안내를 잘 해주셔서 크게 불편하진 않았어요. 다음 행사 때도 꼭 다시 가고 싶습니다.",
        "친구들이랑 {name} 구경 갔다 왔는데 야간에 조명이 켜지니까 분위기가 확 살더라고요. {district} 쪽이라 대중교통으로 접근하기도 좋았고, 사진 찍을 곳도 많아서 만족스러운 하루였습니다.",
    ],
    "레포츠": [
        "{district}에 있는 {name} 코스를 걸어봤는데 생각보다 난이도가 있어서 운동 제대로 됐어요. 경치가 좋아서 힘든 줄 모르고 걸었고, 중간중간 쉴 수 있는 쉼터도 있어서 초보자도 무리 없이 다녀올 수 있을 것 같습니다. 물이랑 편한 신발은 꼭 챙기세요.",
        "{name}에서 주말 아침 라이딩 겸 산책을 했는데 공기도 좋고 사람도 적당해서 쾌적했습니다. {district} 근처에 이런 코스가 있는 줄 몰랐는데 앞으로 자주 이용할 것 같아요.",
        "친구랑 {name}에서 반나절 놀다 왔는데 생각보다 시설이 잘 갖춰져 있어서 놀랐어요. {district} 쪽에서 액티비티 즐기기엔 여기만 한 곳이 없는 것 같습니다. 다음엔 장비 대여도 해봐야겠어요.",
    ],
    "여행코스": [
        "{name} 코스대로 하루 종일 돌아봤는데 동선이 알차게 짜여 있어서 시간 낭비 없이 알찬 하루를 보냈어요. {district} 근처 명소들을 한 번에 둘러볼 수 있어서 여행 계획 짜기 정말 편했습니다. 다음 방문 때도 이 코스 그대로 따라갈 것 같아요.",
        "{district} 당일치기로 {name} 코스를 따라가 봤는데 이동 거리가 적당해서 지치지 않고 다 돌아볼 수 있었습니다. 중간중간 식사할 곳도 코스 안에 잘 껴 있어서 따로 찾아볼 필요가 없었어요.",
        "여행 초행길이라 {name} 코스 그대로 따라갔는데 실패 없는 선택이었어요. {district} 구석구석을 골고루 둘러볼 수 있었고, 각 장소마다 머무는 시간도 적당해서 급하지 않게 여행할 수 있었습니다.",
    ],
}

DEFAULT_CONTENT_TEMPLATES = [
    "지난 주말에 {district}에 있는 {name}에 다녀왔는데 날씨도 좋고 분위기도 좋아서 즐거운 시간을 보냈습니다. 생각했던 것보다 볼거리가 많아서 시간 가는 줄 몰랐어요. 다음에 또 가고 싶습니다.",
    "{name} 처음 방문했는데 {district} 근처에서는 꽤 알려진 곳이더라고요. 여유롭게 둘러보기 좋았고, 사진 찍기 좋은 스팟도 많았습니다. 시간 넉넉하게 잡고 가시는 걸 추천해요.",
    "가족들이랑 {name} 나들이 다녀왔습니다. {district} 쪽이라 이동도 편했고, 아이들도 좋아하고 어른들도 만족스러워하셨어요. 다시 한번 가보고 싶은 곳입니다.",
]

DEFAULT_PASSWORD = "1234"


def extract_district(address: str) -> str:
    """'서울특별시 용산구 한강대로23길 55 (한강로3가)' -> '용산구'"""
    if not address:
        return "서울"
    parts = address.split()
    for part in parts:
        if part.endswith("구") or part.endswith("군"):
            return part
    return parts[0] if parts else "서울"


def seed_posts(count: int):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)

    location_ids = [str(loc_id) for (loc_id,) in db.query(Location.id).all()]
    location_rows = {
        str(loc_id): (name, category, address, image_url)
        for loc_id, name, category, address, image_url in db.query(
            Location.id, Location.name, Location.category, Location.address, Location.image_url
        ).all()
    }

    if not location_ids:
        print("[Warn] locations 테이블이 비어있습니다. 먼저 scripts/seed.py로 장소 데이터를 채워주세요.")
        db.close()
        return

    inserted = 0
    for i in range(count):
        loc_id = random.choice(location_ids)
        loc_name, loc_category, loc_address, loc_image_url = location_rows[loc_id]
        district = extract_district(loc_address)

        content_pool = CONTENT_TEMPLATES_BY_CATEGORY.get(loc_category, DEFAULT_CONTENT_TEMPLATES)

        title = random.choice(TITLE_TEMPLATES).format(name=loc_name)
        content = random.choice(content_pool).format(name=loc_name, district=district)
        author = random.choice(AUTHORS)

        # 장소 이미지가 있으면 80% 확률로 게시글에도 붙여서 실제 서비스처럼 일부만 이미지가 섞이게 함
        image_url = loc_image_url if (loc_image_url and random.random() < 0.8) else None

        post = Post(
            location_id=loc_id,
            title=title,
            content=content,
            author=author,
            password=DEFAULT_PASSWORD,
            image_url=image_url,
        )
        db.add(post)
        inserted += 1

    db.commit()
    db.close()
    print(f"Successfully seeded {inserted} posts into localhub.db!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="posts 테이블에 더미 데이터를 채웁니다.")
    parser.add_argument("--count", type=int, default=200, help="생성할 게시글 개수 (기본 200)")
    args = parser.parse_args()

    seed_posts(args.count)
