from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite 연결을 위한 check_same_thread 옵션 추가
# timeout: 동시 쓰기 시 "database is locked"를 즉시 던지지 않고 잠금 해제를 대기
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 15}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    # SQLite 커넥션은 파일 핸들 수준으로 가벼우므로 풀을 넉넉히 확보.
    # 외부 API 대기 중 세션을 쥐는 패턴은 제거했지만, 순간 동시 접속 폭증에
    # 대비한 안전벨트 (기본 5+10은 데모 트래픽에서도 고갈된 전례 있음)
    pool_size=30,
    max_overflow=60,
)

# SQLite 외래 키(FK) 제약 조건 활성화 (명세 5.2 준수)
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_runtime_columns():
    """기존 SQLite 파일에 나중에 추가된 컬럼을 멱등하게 보강한다.

    Base.metadata.create_all은 없는 '테이블'만 만들 뿐 기존 테이블에 '컬럼'을 추가하지
    않는다. 이미 배포된 localhub.db에는 locations.name_en/address_en 컬럼이 없어
    ORM SELECT가 깨지므로, 앱 시작 시 PRAGMA로 존재 여부를 확인해 없을 때만 ALTER 한다.
    (Alembic 도입 전까지의 경량 마이그레이션. SQLite 외 DB에서는 동작 대상이 아님)
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    from sqlalchemy import text

    required = {
        "locations": {
            "name_en": "VARCHAR(255)",
            "address_en": "VARCHAR(255)",
        },
    }

    with engine.begin() as conn:
        for table, columns in required.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))}
            for column, coltype in columns.items():
                if column not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"))

        # 조회 성능 인덱스 (IF NOT EXISTS라 멱등):
        # 지도 이동마다 도는 bbox·카테고리 필터와 게시글/댓글 집계가 풀스캔을 타지 않도록
        for ddl in (
            "CREATE INDEX IF NOT EXISTS idx_locations_lat_lng ON locations(latitude, longitude)",
            "CREATE INDEX IF NOT EXISTS idx_locations_category ON locations(category)",
            "CREATE INDEX IF NOT EXISTS idx_posts_location ON posts(location_id, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id, is_deleted)",
        ):
            conn.execute(text(ddl))

# DB 세션 의존성 주입용 제너레이터
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
