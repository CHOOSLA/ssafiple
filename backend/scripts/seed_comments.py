"""
posts에 달린 게시글들에 댓글을 채우는 시드 스크립트.

게시글마다 0~4개의 댓글을 무작위로 붙인다. 절반 정도는 장소명을 언급하는
댓글(예: "OOO 저도 가봤는데 좋았어요")을, 나머지는 일반적인 반응/질문 댓글을
섞어서 자연스러운 댓글창 느낌을 낸다. 이미 댓글이 있는 게시글은 건너뛴다.

실행:
    cd backend
    python scripts/seed_comments.py
"""
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models.location import Location
from app.models.post import Post
from app.models.comment import Comment

DEFAULT_PASSWORD = "1234"

COMMENT_AUTHORS = [
    "지나가던행인", "댓글요정", "동네주민2", "강남러버", "궁금이",
    "산책중", "오늘도출근", "주말대기중", "커피한잔", "출근길에",
    "익명의여행자", "동네친구", "직장인B", "취미부자", "느긋하게",
    "오늘의기록", "퇴근후취미", "강남생활자", "가끔들름", "우연히발견",
]

# 장소명을 언급하지 않는 일반 반응/질문 댓글
GENERIC_COMMENTS = [
    "오 저도 가보고 싶었던 곳이에요!",
    "후기 잘 보고 갑니다",
    "사진 보니까 더 궁금해지네요",
    "저도 근처 살아서 자주 지나다녔는데 안 가봤네요",
    "다음 주에 한번 가봐야겠어요",
    "정보 감사합니다 도움 많이 됐어요",
    "오 몰랐던 곳인데 알려주셔서 감사해요",
    "저도 얼마 전에 갔었는데 좋았어요",
    "주차는 어떻게 하셨나요?",
    "영업시간 아시는 분 계신가요",
    "평일에도 사람 많나요?",
    "강추입니다 저도 다녀왔는데 만족했어요",
    "글 잘 읽었습니다 다음에 참고할게요",
    "오 이런 곳이 있었군요 신기하네요",
    "주말에 가봐도 괜찮을까요?",
    "가격대가 궁금하네요",
    "저장해두고 나중에 가봐야겠어요",
    "동네 주민인데 반가운 글이네요",
    "사진 몇 장만 더 볼 수 있을까요",
    "오랜만에 좋은 정보 얻어갑니다",
    "저도 비슷한 경험 있어서 공감돼요",
    "다음엔 저도 데이트 코스로 가봐야겠어요",
    "글 읽으면서 혹했습니다 ㅋㅋ",
    "이 근처 사시나봐요 부럽습니다",
    "자세한 후기 감사해요 도움됐습니다",
    "저는 아직 안 가봤는데 이번 주말에 가보려구요",
    "오 신기하다 이런 데도 있네요",
    "위치 헷갈렸는데 덕분에 잘 찾아갈 수 있을 것 같아요",
    "댓글로 정보 공유해주셔서 감사합니다",
    "저도 다음에 방문해볼게요",
    "사진만 봐도 분위기 좋아 보이네요",
    "오늘 지나가다 봤는데 후기 남겨주셔서 반갑네요",
    "좋은 정보 감사합니다 스크랩해갈게요",
    "저랑 취향이 비슷하신 것 같아요 ㅎㅎ",
    "이 글 보고 바로 검색해봤어요",
]

# 장소명을 넣어 조합하는 댓글 ({name}에 게시글이 연결된 장소명이 들어감)
NAMED_COMMENT_TEMPLATES = [
    "{name} 저도 가봤는데 진짜 좋았어요",
    "{name} 위치가 정확히 어디쯤인가요?",
    "{name} 근처에 주차하기 괜찮나요?",
    "{name} 요즘도 붐비나요?",
    "{name} 다음 주에 가보려고 하는데 시간 여유 있게 잡아야겠네요",
    "{name} 저도 조만간 가볼게요 추천 감사합니다",
    "{name} 사진보다 실물이 더 좋다던데 맞나요?",
    "{name} 처음 들어보는 곳인데 찾아봐야겠어요",
    "{name} 저희 회사에서도 가까워서 가보려구요",
    "{name} 리뉴얼했다는 얘기 들었는데 다녀오셨나봐요",
    "{name} 저도 궁금했던 곳인데 후기 감사합니다",
    "{name} 평 좋다고 들었는데 역시나네요",
    "{name} 이번 주말 코스로 넣어야겠어요",
    "{name} 자세히 써주셔서 도움 많이 됐어요",
    "{name} 저도 한번 가봐야지 하면서 계속 미뤘는데 이제 가봐야겠네요",
]

# 게시글당 댓글 개수 분포 (0개도 자연스럽게 섞이도록)
COUNT_WEIGHTS = [0, 1, 2, 3, 4]
COUNT_PROBS = [0.10, 0.25, 0.30, 0.22, 0.13]


def seed_comments():
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)

    posts = db.query(Post).filter(Post.is_deleted == False).all()
    location_names = {
        loc_id: name for loc_id, name in db.query(Location.id, Location.name).all()
    }

    # 이미 댓글이 달려있는 게시글은 건너뛰어 중복 삽입을 막는다
    posts_with_comments = {
        pid for (pid,) in db.query(Comment.post_id).distinct().all()
    }

    inserted = 0
    skipped_posts = 0
    for post in posts:
        if post.id in posts_with_comments:
            skipped_posts += 1
            continue

        loc_name = location_names.get(int(post.location_id)) if post.location_id else None

        count = random.choices(COUNT_WEIGHTS, weights=COUNT_PROBS, k=1)[0]
        if count == 0:
            continue

        pool = list(GENERIC_COMMENTS)
        if loc_name:
            pool += [t.format(name=loc_name) for t in NAMED_COMMENT_TEMPLATES]

        chosen = random.sample(pool, k=min(count, len(pool)))
        for content in chosen:
            comment = Comment(
                post_id=post.id,
                content=content,
                author=random.choice(COMMENT_AUTHORS),
                password=DEFAULT_PASSWORD,
            )
            db.add(comment)
            inserted += 1

    db.commit()
    db.close()
    print(f"Successfully added {inserted} comments across {len(posts) - skipped_posts} posts "
          f"(skipped {skipped_posts} posts that already had comments).")


if __name__ == "__main__":
    seed_comments()
