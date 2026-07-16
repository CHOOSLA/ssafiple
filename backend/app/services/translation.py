"""UGC 온디맨드 번역(§C-2) 서비스 계층.

게시글/댓글/채팅 등 사용자 생성 콘텐츠를 요청 시점에 번역한다.
동일 원문+대상언어 조합은 translations 테이블에 캐시해 OpenAI 재호출을 막는다.
"""
import hashlib

import openai

from app.core.config import settings
from app.database import SessionLocal
from app.models import Translation

# target_lang 값별 번역 지시. 결과에 따옴표/설명 없이 번역문만 반환하도록 강하게 제약한다.
_LANG_LABEL = {"en": "English", "ko": "Korean"}


def _source_hash(text: str, target_lang: str) -> str:
    """캐시 키. 명세대로 md5(text + target_lang)."""
    return hashlib.md5((text + target_lang).encode("utf-8")).hexdigest()


def _call_openai(text: str, target_lang: str) -> str:
    system_prompt = (
        f"You are a translation engine. Translate the user's text into {_LANG_LABEL[target_lang]}. "
        "Preserve meaning, tone, line breaks, emoji and any URLs. "
        "Return only the translated text with no quotes, notes, or explanations."
    )
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT)
    response = client.chat.completions.create(
        model=settings.OPENAI_TRANSLATE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def translate(text: str, target_lang: str) -> str:
    """캐시를 먼저 조회하고, 없으면 OpenAI로 번역 후 캐시에 저장해 반환한다.

    DB 세션은 캐시 조회/저장 순간에만 짧게 연다 — OpenAI 응답을 기다리는 동안
    커넥션 풀을 점유하면 동시 사용자 몇 명만으로 풀이 고갈된다(QueuePool 장애 원인).

    API 키가 없으면 번역 없이 원문을 그대로 돌려준다(데모 모드, 캐시하지 않음).
    OpenAI 호출 실패는 예외를 그대로 전파하며 라우터가 502로 변환한다.
    """
    source_hash = _source_hash(text, target_lang)

    with SessionLocal() as db:
        cached = db.query(Translation).filter(Translation.source_hash == source_hash).first()
        if cached:
            return cached.translated_text

    if not settings.OPENAI_API_KEY:
        return text

    translated = _call_openai(text, target_lang)

    # 동시 요청이 같은 원문을 번역해 UNIQUE 충돌이 날 수 있으므로, 실패 시 캐시된 값으로 폴백
    with SessionLocal() as db:
        row = Translation(source_hash=source_hash, translated_text=translated)
        db.add(row)
        try:
            db.commit()
        except Exception:
            db.rollback()
            existing = db.query(Translation).filter(Translation.source_hash == source_hash).first()
            if existing:
                return existing.translated_text
            raise

    return translated
