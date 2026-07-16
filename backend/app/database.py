from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite 연결을 위한 check_same_thread 옵션 추가
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
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

# DB 세션 의존성 주입용 제너레이터
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
