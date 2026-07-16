"""
origin/master에 팀원이 커밋한 '경복궁 시연용 데모 게시글 3개 + 댓글 3개'를
현재(강남역 데이터가 채워진) localhub.db에 합쳐 넣는 1회성 스크립트.

origin/master의 backend/localhub.db는 로컬과 독립적으로 갈라져서
(1) 오래된 테스트 쓰레기 게시글 12개("string", "merge-test" 등)와
(2) 실제 시연용으로 작성된 경복궁 게시글 3개(id 13~15, location_id=35)
를 담고 있었다. (1)은 버리고 (2)만 이 DB로 옮겨온다.

실행:
    cd backend
    python scripts/merge_gyeongbok_demo.py
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.post import Post
from app.models.comment import Comment

DEFAULT_PASSWORD = "1234"

# origin/master backend/localhub.db 에서 그대로 가져온 시연용 게시글
GYEONGBOK_POSTS = [
    {
        "title": "경복궁 야간개장 다녀왔어요! 예약 꿀팁 공유",
        "content": "이번 주 야간개장 다녀왔는데 조명 켜진 근정전이 정말 예뻤어요. 예매는 오픈 10분 전에 대기하는 걸 추천합니다. 한복 입으면 무료 입장이라 근처 대여점에서 빌려 입었어요.",
        "author": "궁궐덕후",
        "location_id": "35",
        "comments": [
            ("저도 지난달에 갔는데 야경 진짜 최고였어요!", "달빛나그네"),
            ("한복 대여점 어디 이용하셨는지 알 수 있을까요?", "한복초보"),
        ],
    },
    {
        "title": "평일 오전이 사진 찍기 제일 좋아요",
        "content": "주말엔 사람이 너무 많아서 평일 오전 9시쯤 갔더니 광화문 앞이 한산했어요. 수문장 교대식은 10시, 14시에 하니 시간 맞춰 가보세요.",
        "author": "서울산책러",
        "location_id": "35",
        "comments": [
            ("수문장 교대식 정보 감사합니다. 다음 주에 가보려고요.", "여행준비중"),
        ],
    },
    {
        "title": "외국인 친구 데려가기 좋은 코스 추천",
        "content": "경복궁 → 국립고궁박물관 → 서촌 카페 코스로 반나절 보냈는데 친구가 너무 좋아했어요. 영어 해설 투어도 무료로 운영하니 참고하세요.",
        "author": "가이드지망생",
        "location_id": "35",
        "comments": [],
    },
]


def merge_gyeongbok_demo():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)

    inserted_posts = 0
    inserted_comments = 0
    for item in GYEONGBOK_POSTS:
        post = Post(
            title=item["title"],
            content=item["content"],
            author=item["author"],
            location_id=item["location_id"],
            password=DEFAULT_PASSWORD,
            image_url=None,
        )
        db.add(post)
        db.flush()  # post.id 확보
        inserted_posts += 1

        for content, author in item["comments"]:
            comment = Comment(
                post_id=post.id,
                content=content,
                author=author,
                password=DEFAULT_PASSWORD,
            )
            db.add(comment)
            inserted_comments += 1

    db.commit()
    db.close()
    print(f"Merged {inserted_posts} Gyeongbokgung demo posts and {inserted_comments} comments.")


if __name__ == "__main__":
    merge_gyeongbok_demo()
