# 데이터베이스 스키마 명세 (SCHEMA.md)

데이터베이스: **SQLite** (파일명: `backend/localhub.db`)

> [!NOTE]
> 본 프로젝트는 물리적 삭제 대신 **소프트 딜리트(Soft Delete)** 방식을 채택합니다.
> 이에 따라 테이블에 `is_deleted` 컬럼이 추가되며, 게시글이 Soft Delete 처리될 때 연관 댓글들도 애플리케이션 서비스 로직 수준에서 일괄 Soft Delete(CASCADE) 처리됩니다.

## 테이블 명세

### 1. `locations` (관광지 정보)
JSON 8종 데이터를 기반으로 `seed.py` 스크립트를 통해 최초 적재되는 테이블입니다.

* `id`: INTEGER, PRIMARY KEY, AUTOINCREMENT
* `name`: VARCHAR(255), UNIQUE, NOT NULL - 관광지 명칭
* `category`: VARCHAR(50) - 대분류/분류
* `address`: VARCHAR(255) - 지번/도로명 주소
* `latitude`: DOUBLE - 위도 (서울 지역 검증 범위: `37.40 <= latitude <= 37.72`)
* `longitude`: DOUBLE - 경도 (서울 지역 검증 범위: `126.75 <= longitude <= 127.20`)
* `description`: TEXT, NULL - 설명 (정보가 없는 경우 챗봇 컨텍스트에서 명칭과 주소로 보완)

---

### 2. `posts` (자유게시판 게시글)
* `id`: INTEGER, PRIMARY KEY, AUTOINCREMENT
* `title`: VARCHAR(255), NOT NULL - 제목
* `content`: TEXT, NOT NULL - 내용
* `author`: VARCHAR(50), NOT NULL - 작성자 닉네임
* `password`: VARCHAR(255), NOT NULL - **평문 비밀번호** (명세 제약조건에 따라 암호화하지 않고 저장)
* `image_url`: VARCHAR(255), NULL - 업로드된 이미지 파일 경로 (P2 기능)
* `is_deleted`: BOOLEAN, DEFAULT FALSE - 소프트 딜리트 여부
* `created_at`: DATETIME, DEFAULT CURRENT_TIMESTAMP - 생성 일시
* `updated_at`: DATETIME, DEFAULT CURRENT_TIMESTAMP - 수정 일시

---

### 3. `comments` (게시판 댓글)
* `id`: INTEGER, PRIMARY KEY, AUTOINCREMENT
* `post_id`: INTEGER, FOREIGN KEY REFERENCES `posts(id)` - 대상 게시글 ID
* `content`: TEXT, NOT NULL - 댓글 내용
* `author`: VARCHAR(50), NOT NULL - 작성자 닉네임
* `password`: VARCHAR(255), NOT NULL - **평문 비밀번호**
* `is_deleted`: BOOLEAN, DEFAULT FALSE - 소프트 딜리트 여부
* `created_at`: DATETIME, DEFAULT CURRENT_TIMESTAMP - 생성 일시
