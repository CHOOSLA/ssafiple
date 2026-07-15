---
title: 데이터베이스 및 시딩 제약사항
---

테이블 컬럼 명세는 [docs/SCHEMA.md](../../docs/SCHEMA.md) 참고.

## Soft Delete 기반 연쇄(CASCADE) 처리
* 물리적 삭제(`DELETE`)를 배제하고, `is_deleted = True` 플래그를 업데이트하는 소프트 딜리트 방식을 적용합니다.
* 게시글이 Soft Delete 처리될 경우, 해당 게시글에 종속된 모든 댓글도 연쇄(CASCADE)적으로 `is_deleted = True` 처리되도록 백엔드 비즈니스 로직에서 구현합니다.
* 모든 데이터 조회(목록/상세) 시 `is_deleted = False`인 데이터만 필터링하여 노출합니다.

## 위도/경도(좌표) 뒤바뀜 방지 검증 (Assert)
* 공공데이터 JSON의 지리 정보(`mapx`, `mapy`) 적재 시 위도·경도가 뒤바뀌는 사고가 빈번합니다.
* `backend/scripts/seed.py`에서 데이터를 파싱·적재할 때 서울 권역 경계선(Bounding Box) 범위 검증을 강제(assert)로 수행합니다.
  * 경도(Longitude): `126.75 <= longitude <= 127.20`
  * 위도(Latitude): `37.40 <= latitude <= 37.72`
