"""
실제 웹 검색으로 확인한 사실관계(운영시간, 최근 행사, 매장 특징 등)를 바탕으로
새로 작성한 게시글을 채우는 시드 스크립트. 강남역 인근의 잘 알려진 장소 13곳을
대상으로 하며, 기존 게시글을 대체하지 않고 추가한다.

각 게시글의 내용은 실제 리뷰를 복사/각색한 것이 아니라, 검색으로 확인한 사실을
근거로 새로 집필한 글이다. 이미지도 해당 장소의 실제 사진(TourAPI 원본 및
Wikimedia Commons)만 사용한다.

실행:
    cd backend
    python scripts/seed_posts_researched.py
"""
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.post import Post
from app.models.post_image import PostImage

DEFAULT_PASSWORD = "1234"

AUTHORS = [
    "역삼직장인", "강남토박이", "테헤란로러너", "주말산책러", "골목탐방가",
    "문화생활러", "출장러", "강남워커", "혼자여행", "동네주민",
]

# (location_id, 제목, 본문, [이미지 URL, ...])
RESEARCHED_POSTS = [
    (1244, "국기원 2026 세계태권도한마당 다녀왔어요",
     "8월 초 국기원에서 열린 세계태권도한마당 구경하러 갔는데, 품새·격파·시범이 하루 종일 이어져서 시간 가는 줄 몰랐습니다. 외국인 참가자들도 정말 많아서 태권도가 국제적으로 얼마나 사랑받는지 실감했어요. 참가 신청은 홈페이지에서 미리 받는다고 하니, 직접 겨루기까지 해보고 싶으신 분들은 다음 대회 일정을 챙겨보시는 걸 추천드립니다. 시범 공연만 구경해도 충분히 볼거리가 많았어요.",
     [
         "http://tong.visitkorea.or.kr/cms/resource/96/3567696_image2_1.jpg",
         "https://commons.wikimedia.org/wiki/Special:FilePath/Kukkiwon_(2019).jpg",
         "https://commons.wikimedia.org/wiki/Special:FilePath/Kukkiwon-gates-2010.jpg",
     ]),
    (1619, "라인프렌즈 강남 플래그십 BT21·미니니 굿즈 구경 다녀왔어요",
     "서초동 매장인데 대형 스크린에서 애니메이션이 계속 나오고 있어서 들어서자마자 눈이 즐거웠습니다. BT21이랑 미니니, TRUZ 캐릭터 라인이 특히 잘 꾸며져 있었고, 한국에서만 살 수 있는 한정 굿즈도 있어서 외국인 친구 선물로 몇 개 샀어요. 분기마다 다른 브랜드랑 콜라보 팝업도 연다고 하니, 갈 때마다 새로운 걸 볼 수 있을 것 같습니다.",
     ["https://tong.visitkorea.or.kr/cms/resource/20/4054220_image2_1.jpeg"]),
    (5813, "조선 팰리스 24층 1914 라운지앤바 애프터눈티 후기",
     "기념일이라 큰맘 먹고 24층 1914 라운지앤바에서 애프터눈티를 즐겼는데, 2인 세트가 12만원(부가세 포함)이었고 예약금 5만원을 미리 결제해야 했어요. 3단 트레이에 담긴 핑거푸드랑 티가 알차게 나왔고, 통유리 너머로 보이는 서울 전망이 정말 좋았습니다. 주차는 3시간 무료라 부담 없었고, 예약은 필수라는 점 참고하세요.",
     ["https://tong.visitkorea.or.kr/cms/resource/05/2786805_image2_1.jpg"]),
    (704, "일상비일상의틈 7층 다 둘러봤어요 (강남역 3분 거리)",
     "강남역에서 걸어서 3분이면 도착하는 LG유플러스 브랜드 공간인데, 지하 1층부터 5층까지 층마다 컨셉이 완전히 달라요. 1층은 팝업스토어, 2층은 서핑 테마 카페, 3~4층은 독립서점이랑 포토 스튜디오라 층별로 사진 찍는 재미가 있었습니다. 약속 전에 잠깐 들르기 딱 좋은 위치예요.",
     [
         "http://tong.visitkorea.or.kr/cms/resource/10/3354010_image2_1.jpg",
         "https://commons.wikimedia.org/wiki/Special:FilePath/Gangnam-station-entrance-12-20181121-143234.jpg",
     ]),
    (6476, "케미스트릿 팝업, K-맛·K-멋·K-미 다 즐기고 왔어요",
     "서울시 로컬브랜드 상권 육성사업으로 여는 축제라는데, 강남역 보행광장에 청년 타깃 체험 부스가 쭉 늘어서 있었습니다. 거리 노래방이랑 디제잉하는 서브무대도 있어서 구경하는 재미가 있었고, 로컬 브랜드들 체험존도 알차게 꾸며져 있었어요. 강남역 나오자마자 바로 보이는 위치라 접근성도 좋았습니다.",
     [
         "http://tong.visitkorea.or.kr/cms/resource/55/3520355_image2_1.jpg",
         "https://commons.wikimedia.org/wiki/Special:FilePath/Seoul-metro-222-Gangnam-station-sign-20181121-142734.jpg",
     ]),
    (6399, "케미스트릿 강남역 페스티벌, 서초동 BLOCK 77 쪽도 다녀왔어요",
     "봉은사로 쪽 팝업이랑은 별개로 서초구에서 여는 페스티벌인데, 서초·강남역 상권에 활력을 불어넣기 위한 행사라고 하더라고요. 부스 구성이 팝업이랑은 또 달라서 두 곳 다 돌아다니면 하루 종일 알차게 즐길 수 있을 것 같습니다.",
     ["http://tong.visitkorea.or.kr/cms/resource/64/3553464_image2_1.jpg"]),
    (1655, "나이키 강남 리뉴얼 매장, 나이키 바이 유 커스텀 해봤어요",
     "작년 5월에 리뉴얼 오픈한 3층 규모 매장인데, 2층 나이키 바이 유(Nike By You) 존에서 제가 산 신발에 프린팅이랑 액세서리를 조합해서 커스텀했습니다. 세상에 하나뿐인 신발이 된 느낌이라 만족스러웠어요. 매장은 10:30~22:00까지 운영하니 여유 있게 방문하시는 걸 추천드립니다.",
     ["https://tong.visitkorea.or.kr/cms/resource/51/4044051_image2_1.png"]),
    (2552, "아트박스 강남점 영업시간 확인하고 가세요 (11시~22시30분)",
     "테헤란로1길에 있는 매장인데 오전 11시부터 밤 10시 30분까지 운영해서 퇴근하고 들르기 좋았습니다. 다이어리 시즌 소품부터 캐릭터 문구까지 알차게 진열되어 있어서 구경하다 보면 시간 금방 가요. 저녁 시간대에도 사람이 꽤 있는 편이라 여유 있게 둘러보고 싶으면 평일 오전을 추천드립니다.",
     ["https://tong.visitkorea.or.kr/cms/resource/77/4043177_image2_1.jpg"]),
    (974, "국립어린이청소년도서관 실감놀이 체험, 둘째 월요일은 휴관이에요",
     "테헤란로7길에 있는 도서관인데 09:00~18:00 운영하고, 매월 둘째·넷째 월요일은 휴관이라 가시기 전에 꼭 확인하세요. 혼합현실·확장현실 체험하는 '미꿈소' 프로그램이랑 실감놀이 코너가 있어서 아이가 책만 보는 게 아니라 체험형으로 놀 수 있었습니다. 첨단기술 체험 프로그램도 종종 열리니 홈페이지에서 일정 확인하고 가시는 걸 추천드려요.",
     ["https://tong.visitkorea.or.kr/cms/resource/93/3386193_image2_1.JPG"]),
    (6417, "서리풀뮤직페스티벌, 반포대로 차 없는 거리로 다녀왔어요",
     "매년 9월에 열리는 축제인데, 서초역부터 서초3동사거리까지 약 900m 구간을 차 없는 거리로 통제하고 진행합니다. 클래식의 밤부터 재즈 나이트, K-POP의 밤까지 이틀 동안 프로그램이 알차게 이어졌고, 대부분 무료 관람이라 부담 없이 즐길 수 있었어요. 마지막 날 불꽃놀이까지 보고 나니 여름 끝자락을 제대로 즐긴 기분이었습니다.",
     ["http://tong.visitkorea.or.kr/cms/resource/08/3354108_image2_1.jpg"]),
    (5717, "논현 가구거리 신혼집 가구 보러 다녀왔어요 (매장 70곳 이상)",
     "학동로를 따라 가구 매장이 70개 넘게 늘어서 있다고 하는데, 실제로 걸어보니 정말 끝이 안 보일 정도였습니다. 1970년대부터 형성된 거리라 오래된 노하우가 있는 매장들도 많고, 1996년에 강남구에서 가구 문화 특화 거리로 지정했다고 하더라고요. 논현역이랑 학동역 사이라 대중교통으로 이동하기도 편했습니다.",
     ["http://tong.visitkorea.or.kr/cms/resource/28/3571728_image2_1.jpg"]),
    (627, "우면산 소망탑 야경 명소, 해질녘에 가세요",
     "정상까지 성인 기준 1시간 남짓이면 오를 수 있는 완만한 코스라 초보자도 부담 없었습니다. 방문객들이 하나둘 돌을 쌓아 만든 소망탑이 정상에 있는데, 해가 기울기 시작할 무렵 올라가서 돌 하나 얹고 소원 빌고 나니 곧 서울 전역의 야경이 펼쳐졌어요. 남산처럼 붐비지 않아서 한적하게 야경 즐기기엔 여기가 훨씬 좋은 것 같습니다.",
     ["http://tong.visitkorea.or.kr/cms/resource/59/3467859_image2_1.jpg"]),
    (3124, "삼성 강남, 8K 미디어아트 더 월(The Wall) 보고 왔어요",
     "2023년에 기존 딜라이트샵을 대체해서 새로 연 체험형 플래그십 매장인데, 갤럭시 시리즈 위주로 제품 카테고리를 정리해서 그런지 훨씬 둘러보기 편했습니다. 입구의 초대형 8K 디스플레이 '더 월'에서 강남대로 마천루를 표현한 미디어아트가 나오는데, 그것만 봐도 눈이 즐거워요. 신제품 체험 프로그램도 있으니 기변 고민 중이시면 들러보시는 걸 추천드립니다.",
     ["https://tong.visitkorea.or.kr/cms/resource/18/4043818_image2_1.png"]),
]


def seed_researched_posts():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)

    inserted_posts = 0
    inserted_images = 0
    for location_id, title, content, image_urls in RESEARCHED_POSTS:
        post = Post(
            location_id=str(location_id),
            title=title,
            content=content,
            author=random.choice(AUTHORS),
            password=DEFAULT_PASSWORD,
            image_url=image_urls[0] if image_urls else None,
        )
        db.add(post)
        db.flush()
        inserted_posts += 1

        for order, url in enumerate(image_urls):
            db.add(PostImage(post_id=post.id, image_url=url, display_order=order))
            inserted_images += 1

    db.commit()
    db.close()
    print(f"Successfully added {inserted_posts} researched posts with {inserted_images} images.")


if __name__ == "__main__":
    seed_researched_posts()
