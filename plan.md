# LocalHub — 8시간 구현 계획서 (plan.md)

> 이 문서는 **계획 전용**이다. 코드는 아직 한 줄도 변경하지 않았다. 아래 내용은 `research.md`(현 코드베이스 분석)를 기반으로, `backend/app/*`와 `frontend/src/*`의 실제 소스를 읽고 도출한 구체적 실행 계획이다.

> **변경 이력(2026-07-15 피드백 반영)**
> 1. **게시판(2절) 구현 보류** — CRUD 게시판은 다른 팀원이 별도로 구현하기로 함. 계획 문서(2절)는 팀원과의 인터페이스 합의/인수인계 참고용으로 **그대로 보관**하되, 이번 8시간 실행 범위(0. 타임라인)에서는 **제외**한다.
> 2. ~~챗봇에 프리셋 질문 유형(페르소나/카테고리 칩) 추가~~ → **3번 피드백으로 대체/구체화됨.** "가족/연인/혼자"처럼 사람 중심으로 카테고리를 고르게 하던 1차 설계는, 서비스의 메인 데이터가 축제라는 3번 피드백에 맞춰 **"축제 먼저 선택 → 그 축제 주변 카테고리를 순차로 질문"**하는 흐름으로 재설계되었다(아래 3번 참고, 1절/3절 본문에 반영).
> 3. **챗봇 플로우를 "축제 우선 추천 → 주변 시설 카테고리 follow-up → 거리순 추천"으로 재설계** — 메인 데이터가 축제공연행사이므로, 챗봇은 ① 먼저 축제 후보를 추천하고 ② 사용자가 축제 하나를 고르면 "주변에 또 어떤 시설이 궁금한가요?"라고 되물어 숙박/문화시설/쇼핑/레포츠/관광지 중 카테고리를 고르게 한 뒤 ③ 그 축제 좌표를 기준으로 실제 거리(km) 순으로 정렬한 결과를 추천한다. 1절(RAG 백엔드)과 3절(챗봇 UI)을 이 흐름에 맞춰 전면 재작성했다.
> 4. **1단계(축제 추천)에서도 자유 텍스트에 담긴 지역/동행 힌트를 반영** — 사용자가 "강남 근처 가족이랑 갈만한 축제"처럼 지역이나 분위기(가족/연인/친구/혼자)를 문장에 포함하면, 1단계 축제 후보 검색이 이를 반영해 후보를 고르거나 우선순위를 조정한다. 지역은 기존 키워드 검색(제목/주소 LIKE)이 이미 처리하고, 동행 힌트는 새로 추가한 경량 키워드 사전으로 후보를 재정렬한다(1-3절 `detect_companion_hint`). 이후 2·3단계(카테고리 follow-up → 거리순 추천) 흐름은 그대로 유지한다.
> 게시판 보류로 비는 시간은 챗봇 플로우 고도화 및 QA/문서화 버퍼로 재배분했다(아래 타임라인 참고).

## 0. 전제 확인 (실행 전 반드시 재확인)

- 대상 백엔드는 **`backend/app/`** (포트 8001, `app.` 패키지 import, `Base`/`SessionLocal`은 `backend/app/orm.py`)이다. `project/`(포트 8000, 구버전 스크립트)는 이번 8시간 범위에서 **건드리지 않는다** — 손댈 시간 대비 리스크가 큼.
- DB 파일은 `project/seoul_festival.db` (`orm.py`의 `DB_PATH = .../project/seoul_festival.db`)를 그대로 재사용한다. 이미 `places` 테이블에 서울 6개 카테고리(관광지/문화시설/축제/레포츠/숙박/쇼핑, `content_type_id` 12/14/15/28/32/38)가 적재되어 있음(`import_seoul_data.py` 실행 이력 존재, `project/seoul_festival.db` 파일 존재 확인됨).
- 프론트는 `frontend/vite.config.js`에서 `/api` → `http://127.0.0.1:8001` 프록시. 신규 API는 전부 **`/api/...`** 프리픽스로 통일한다(기존 `/festivals`, `/nearby`, `/chat` 등 프리픽스 없는 레거시 JSON 엔드포인트는 **그대로 둔다** — 삭제/정리는 8시간 범위 밖, `research.md` 7절 기술부채로 남김).
- `OPENAI_API_KEY`는 `.env`(백엔드 실행 디렉터리 또는 `backend/.env`)로 로컬에 설정되어 있어야 함. `.env`는 이미 `.gitignore`에 포함되어 있으므로 새로 만들되 커밋 금지.

## 8시간 타임라인 (권장 배분, 게시판 제외 반영)

| 구간 | 작업 | 산출물 |
|---|---|---|
| 0:00–0:20 | 환경 점검(DB 존재, `OPENAI_API_KEY`, `openai` 패키지 버전, 팀원과 게시판 API 계약(`/api/posts/*`) 공유) | 체크리스트 통과 |
| 0:20–2:30 | ① OpenAI 마이그레이션 + 간이 RAG `/api/chat` (축제 탐색 + 축제앵커 기반 카테고리별 거리순 조회) | 백엔드 챗봇 동작 확인(Swagger/curl) |
| 2:30–4:30 | ③ 챗봇 프론트 UI(`ChatWidget.vue`) — 축제 선택 → 카테고리 follow-up → 거리순 결과 3단계 플로우 연동 | 브라우저에서 축제 선택→카테고리 선택→거리순 리스트 확인 |
| 4:30–5:30 | ④ `npm run build` → FastAPI 단일 포트 서빙 | `http://localhost:8001` 하나로 전체 접속 |
| 5:30–7:00 | 여유 버퍼 — 챗봇 프롬프트/UX 다듬기, 게시판 병합 대비 라우팅·네비게이션 정리, 회귀 테스트 | 안정화 |
| 7:00–8:00 | 통합 QA, README/실행법 갱신, 최종 커밋 | 제출 가능 상태 |

> ② 게시판은 이번 타임라인에서 **제외**되었다(다른 팀원 담당). 아래 2절 계획은 실행하지 않고 **문서로만 보관**한다 — 팀원이 동일한 API 설계(엔드포인트/스키마)를 그대로 쓰거나 참고할 수 있도록 유지.

---

## 1. OpenAI 클라이언트 마이그레이션 + 간이 RAG 챗봇

### 1-1. 문제 진단 (재확인)

`backend/app/openai_client.py`는 openai 0.x 레거시 전역 API(`openai.api_key = ...`, `openai.ChatCompletion.create(...)`)를 사용 중이나 `backend/requirements.txt`는 `openai>=1.0.0`을 명시한다. 1.0+ SDK에는 `ChatCompletion` 클래스가 없어 `AttributeError: module 'openai' has no attribute 'ChatCompletion'`로 즉시 실패한다. **최우선 수정 대상.**

또한 현재 `/chat`(main.py:146)은 `data_store.search_festival` + `data_store.nearby_items`로 **JSON 인메모리 데이터**를 컨텍스트로 쓴다. 요구사항은 "SQLite DB에 저장된 축제 목록 데이터를 쿼리"하는 RAG이므로, 신규 엔드포인트 `POST /api/chat`은 **DB(`places` 테이블)를 직접 쿼리**하도록 새로 구현한다. 기존 `POST /chat`(JSON 기반)은 건드리지 않고 그대로 둔다(레거시로 남김, 프론트도 이걸 호출하지 않음).

**(피드백 반영) 챗봇 대화 플로우 재설계**: 서비스의 메인 데이터는 축제공연행사(`content_type_id=15`)다. 챗봇은 자유 텍스트 한 번으로 아무 카테고리나 뒤섞어 답하지 않고, 아래 **3단계 플로우**를 따른다.

1. **축제 탐색**: 사용자의 질문(예: "이번 주말 축제 추천해줘")으로 축제만 검색해 후보 목록을 제시한다.
2. **축제 선택 → 카테고리 follow-up**: 사용자가 후보 중 하나를 고르면, "이 축제 주변에 또 어떤 시설이 궁금한가요?"라고 되물으며 숙박/문화시설/쇼핑/레포츠/관광지 중 고르게 한다(이 단계는 백엔드 호출 없이 프론트에서 즉시 처리 — 3-1절 참고).
3. **거리순 추천**: 선택된 카테고리가 오면, **선택된 축제의 좌표를 앵커(anchor)** 로 삼아 같은 카테고리의 장소를 실제 거리(km) 기준으로 정렬해 추천한다.

이 플로우는 `services.py`의 기존 `fetch_nearby_places`(축제 기준 주변장소, 제곱거리 근사)와 `data_loader.py`의 `nearby_itinerary`(축제 기준 주변장소, 정확한 haversine)가 이미 시도했던 "축제 앵커 + 주변 카테고리" 개념을 그대로 계승하되, DB 기반으로 통일하고 대화형 후속 질문(follow-up) 형태로 사용자 경험을 다듬은 것이다.

### 1-2. `backend/app/openai_client.py` — 전면 교체

```python
import os
from typing import Dict, List

from openai import OpenAI


class OpenAIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self._client: OpenAI | None = OpenAI(api_key=self.api_key) if self.api_key else None

    def ensure_api_key(self) -> None:
        if not self._client:
            raise RuntimeError(
                "OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다. .env 또는 실행 환경에 키를 추가하세요."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.5,
        max_tokens: int = 500,
    ) -> str:
        self.ensure_api_key()
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
```

**변경 요점**: 전역 `openai.api_key` 대신 인스턴스 `OpenAI(api_key=...)` 클라이언트 사용, `openai.ChatCompletion.create` → `client.chat.completions.create`, 응답 접근 경로(`response.choices[0].message.content`)는 1.x에서도 동일하므로 유지. 모델은 `gpt-3.5-turbo` 유지해도 무방하나, 비용/품질 균형 상 `gpt-4o-mini` 권장(트레이드오프는 1-6절 참조).

### 1-3. RAG 검색 파이프라인 — `backend/app/services.py`에 함수 추가

**설계 결정**: SQLite에서 삼각함수(haversine)를 직접 계산하는 대신, ① **바운딩 박스(위경도 범위)로 1차 필터** → SQL 인덱스(`idx_places_geo`)를 활용해 후보군을 좁히고, ② Python에서 정확한 haversine으로 정렬 — 이렇게 2단계로 나누면 전체 테이블 스캔 없이 효율적으로 "가까운 장소"를 뽑을 수 있다(`data_loader.py`에 이미 있는 haversine 함수를 재사용). 이번 피드백에 따라 이 파이프라인은 **두 개의 함수**로 나뉜다 — ① 축제만 검색하는 `search_festivals_for_chat`(1단계), ② 선택된 축제의 좌표를 앵커로 주변 카테고리를 거리순 정렬하는 `nearby_by_category_from_anchor`(3단계).

키워드 검색은 형태소 분석기 등 외부 라이브러리 추가 없이, 질문 문자열에서 공백 기준 토큰을 뽑고 2글자 이상인 토큰만 `LIKE` 조건으로 title/address1에 매칭한다(간단하지만 8시간 제약에 맞는 실용적 선택). **이 키워드 검색이 title뿐 아니라 address1도 함께 보기 때문에, "강남 축제 추천해줘"처럼 지역이 문장에 들어있으면 별도 로직 없이도 이미 그 지역 축제가 우선 매칭된다** — 피드백의 "지역 제시" 부분은 기존 구조로 충족됨.

**(피드백 반영) 동행/분위기 힌트 감지**: "가족이랑 갈만한", "연인과", "친구들이랑" 같은 표현이 질문에 있으면, 이를 감지해 ①후보 재정렬에 반영하고 ②1단계 프롬프트에 컨텍스트로 덧붙인다. TourAPI 원본 스키마(`data/서울/SCHEMA.md`)에는 "가족 친화" 같은 명시적 태그 필드가 없으므로, 완벽한 필터링은 불가능하다 — 아래 구현은 **제목에 관련 단어가 포함된 축제를 후보 앞쪽으로 재정렬하는 휴리스틱**이며, 매칭이 없으면 원래 순서를 그대로 유지하는 "있으면 좋고 없어도 무방한" 보강 로직이다(정확도를 보장하는 하드 필터가 아님을 1-3절 트레이드오프에 명시).

```python
# backend/app/services.py 에 추가

import re
from math import radians, sin, cos, asin, sqrt
from typing import Optional, Tuple
from sqlalchemy import or_


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def _extract_keywords(question: str) -> List[str]:
    tokens = re.split(r"[\s,.!?~]+", question.strip())
    return [t for t in tokens if len(t) >= 2][:5]


# content_type_id: 12=관광지, 14=문화시설, 15=축제, 28=레포츠, 32=숙박, 38=쇼핑
CATEGORY_LABEL_MAP = {
    "관광지": [12],
    "문화시설": [14],
    "레포츠": [28],
    "숙박": [32],
    "쇼핑": [38],
}

# 자유 텍스트에서 동행/분위기를 감지하기 위한 경량 키워드 사전(형태소 분석기 없이 substring 매칭)
COMPANION_HINT_KEYWORDS = {
    "가족": ["가족", "아이랑", "아이와", "아이들", "키즈", "패밀리"],
    "연인": ["연인", "커플", "데이트", "남자친구", "여자친구"],
    "친구": ["친구"],
    "혼자": ["혼자", "나홀로", "솔로"],
}


def detect_companion_hint(question: str) -> Optional[str]:
    for hint, words in COMPANION_HINT_KEYWORDS.items():
        if any(word in question for word in words):
            return hint
    return None


def search_festivals_for_chat(
    question: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    limit: int = 8,
) -> List[Place]:
    """1단계: 자유 텍스트 질문으로 '축제(15)'만 검색한다. 지역은 title/address1 LIKE로,
    동행 힌트는 제목 재정렬 휴리스틱으로 반영한다."""
    db: Session = SessionLocal()
    try:
        candidates: dict[int, Place] = {}

        keywords = _extract_keywords(question)
        if keywords:
            query = db.query(Place).filter(Place.content_type_id == 15)
            like_conditions = [Place.title.like(f"%{kw}%") for kw in keywords] + \
                               [Place.address1.like(f"%{kw}%") for kw in keywords]
            rows = query.filter(or_(*like_conditions)).limit(limit).all()
            for row in rows:
                candidates[row.place_id] = row

        # 키워드 매칭이 없으면(또는 부족하면) 최신 축제 순으로 보충 — 챗봇이 항상 뭔가는 추천하도록
        if len(candidates) < limit:
            fallback_rows = (
                db.query(Place)
                .filter(Place.content_type_id == 15)
                .order_by(Place.place_id.desc())
                .limit(limit - len(candidates))
                .all()
            )
            for row in fallback_rows:
                candidates.setdefault(row.place_id, row)

        results = list(candidates.values())

        # 동행 힌트가 감지되면, 제목에 관련 단어가 포함된 후보를 앞으로 재정렬(매칭 없으면 순서 그대로 유지)
        companion_hint = detect_companion_hint(question)
        if companion_hint:
            hint_words = COMPANION_HINT_KEYWORDS[companion_hint]
            results.sort(key=lambda p: not any(w in p.title for w in hint_words))

        # 사용자 위치가 있으면 가까운 축제를 우선 노출(정렬만 다시 함, 동행 힌트 재정렬보다 우선)
        if lat is not None and lon is not None:
            results.sort(
                key=lambda p: _haversine_km(lat, lon, p.latitude, p.longitude) if p.latitude and p.longitude else 9e9,
            )

        return results[:limit]
    finally:
        db.close()


def get_place(place_id: int) -> Optional[Place]:
    db: Session = SessionLocal()
    try:
        return db.query(Place).filter(Place.place_id == place_id).first()
    finally:
        db.close()


def nearby_by_category_from_anchor(
    anchor: Place,
    category: str,
    limit: int = 5,
    delta: float = 0.1,  # 약 11km 대응 바운딩 박스 — 축제 주변을 넉넉히 훑기 위해 1-3절 사용자 위치 검색(0.05)보다 넓게 잡음
) -> List[Tuple[Place, float]]:
    """3단계: 선택된 축제(anchor) 주변에서 지정 카테고리를 거리순으로 반환한다."""
    allowed_types = CATEGORY_LABEL_MAP.get(category)
    if not allowed_types or anchor.latitude is None or anchor.longitude is None:
        return []

    db: Session = SessionLocal()
    try:
        rows = (
            db.query(Place)
            .filter(Place.content_type_id.in_(allowed_types))
            .filter(Place.place_id != anchor.place_id)
            .filter(Place.latitude.between(anchor.latitude - delta, anchor.latitude + delta))
            .filter(Place.longitude.between(anchor.longitude - delta, anchor.longitude + delta))
            .limit(200)
            .all()
        )
        scored = [
            (row, _haversine_km(anchor.latitude, anchor.longitude, row.latitude, row.longitude))
            for row in rows
        ]
        scored.sort(key=lambda pair: pair[1])
        return scored[:limit]
    finally:
        db.close()
```

> **트레이드오프(거리 계산)**: SQLite는 네이티브 지리공간 함수가 없어 진짜 haversine을 SQL 레벨에서 못 돌린다. 바운딩 박스 사전 필터 + Python 정렬 조합은 "정확도 vs 구현 난이도"의 실용적 절충안이다. 데이터 규모(서울 기준 places 수천 건)에서는 인덱스(`idx_places_geo`)만으로 충분히 빠르다. 완전한 정확도가 필요하면 `sqlite-vss`나 raw SQL의 `ORDER BY (lat-?)*(lat-?)+(lon-?)*(lon-?) LIMIT n`(이미 `services.py`의 `fetch_nearby_places`가 쓰는 방식) 근사식을 그대로 재사용해도 되지만, 이번엔 정확한 km 단위 정렬을 우선했다.
>
> **트레이드오프(지역 선택 미지원)**: 현재 `places` 테이블에는 **서울 데이터만** 적재되어 있다(`import_seoul_data.py`가 서울 JSON만 처리, `DATA_ROOT`도 서울 고정 — `research.md` 3절 참조). 다른 4개 권역(부산/대전_충청권/구미_경북권/광주_전라권) JSON은 아직 DB로 적재되지 않았으므로, 이번 8시간 범위에서는 서울 축제만 다룬다. **서울 안에서 "강남", "홍대"처럼 동/구 단위 지역을 문장에 언급하는 것은 이미 `search_festivals_for_chat`의 title/address1 키워드 검색으로 반영된다** — 별도 구현이 필요한 건 다른 시/도(부산 등) 전체를 바꾸는 경우뿐이다. 그러려면 ①해당 권역 JSON을 `import_seoul_data.py`와 동일한 패턴으로 추가 적재하고 ②`regions` 테이블 기준 필터를 추가해야 하며, 이는 8시간 스코프 밖의 후속 작업으로 남긴다.
>
> **트레이드오프(동행 힌트는 정확한 필터가 아님)**: `detect_companion_hint`는 질문 문장에서 "가족/연인/친구/혼자" 관련 단어를 감지해 **제목에 같은 단어가 들어간 축제를 앞으로 재정렬**할 뿐, TourAPI 데이터에 그런 속성 자체가 없어 "이 축제가 실제로 가족 단위에 적합한지"는 판단하지 못한다. 즉 완벽한 개인화 필터가 아니라 "맞으면 좋고 안 맞아도 순서만 그대로일 뿐 손해는 없는" 저위험 보강 로직이다. 더 정교하게 하려면 축제 설명 텍스트에 대한 LLM 분류(추가 API 호출 필요)나 카테고리 태그 데이터 보강이 필요하며, 8시간 범위에서는 과합이라 채택하지 않았다.

### 1-4. 신규 엔드포인트 — `backend/app/main.py`

```python
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ApiChatRequest(BaseModel):
    question: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    festival_id: Optional[int] = None  # 2단계에서 사용자가 고른 축제(앵커)
    category: Optional[str] = None     # 3단계에서 고른 카테고리: "관광지" | "문화시설" | "레포츠" | "숙박" | "쇼핑"
    history: List[ChatMessage] = []    # 프론트에서 이전 대화 turn을 함께 전달(간단 히스토리 유지)


class ChatSourceOut(BaseModel):
    id: int
    title: str
    address: Optional[str] = None
    tel: Optional[str] = None
    category: Optional[int] = None
    distance_km: Optional[float] = None  # 3단계(앵커 기준 거리순)에서만 채워짐


class ApiChatResponse(BaseModel):
    answer: str
    sources: List[ChatSourceOut]


def build_festival_prompt(question: str, festivals: List[Place], companion_hint: Optional[str] = None) -> str:
    """1단계 프롬프트: 축제 후보를 소개하고 하나를 골라보라고 안내."""
    if not festivals:
        source_text = "현재 조건에 맞는 축제 데이터를 찾지 못했습니다."
    else:
        source_text = "\n".join(
            f"- {p.title} | 주소: {p.address1 or '정보 없음'} | 전화: {p.tel or '정보 없음'}"
            for p in festivals
        )
    hint_line = f"사용자가 언급한 동행/분위기: {companion_hint}\n" if companion_hint else ""
    return (
        "당신은 서울 지역 축제 정보를 추천하는 챗봇입니다. "
        "아래 축제 데이터 소스를 근거로만 답하고, 소스에 없는 내용은 추정하지 마세요.\n\n"
        f"{hint_line}"
        f"사용자 질문: {question}\n\n---\n축제 후보:\n{source_text}\n---\n"
        "한국어로 후보를 간단히 소개하고, 마음에 드는 축제를 하나 선택해달라고 안내하세요. "
        "동행/분위기가 언급되었다면 그에 어울리는 후보를 먼저 언급하되, 후보 목록에 없는 내용은 지어내지 마세요."
    )


def build_nearby_prompt(anchor: Place, category: str, scored: List[Tuple[Place, float]]) -> str:
    """3단계 프롬프트: 앵커 축제 주변의 거리순 결과를 그대로 안내."""
    if not scored:
        source_text = f"'{anchor.title}' 주변에서 '{category}' 데이터를 찾지 못했습니다."
    else:
        source_text = "\n".join(
            f"- {p.title} ({d:.1f}km) | 주소: {p.address1 or '정보 없음'} | 전화: {p.tel or '정보 없음'}"
            for p, d in scored
        )
    return (
        f"당신은 '{anchor.title}' 축제 주변 정보를 안내하는 챗봇입니다. "
        f"사용자가 이 축제 주변의 '{category}' 정보를 원합니다. "
        "아래 후보를 이미 거리가 가까운 순서로 정렬했으니 그 순서를 유지해서 안내하고, "
        "소스에 없는 내용은 추정하지 마세요.\n\n"
        f"---\n{source_text}\n---\n한국어로 간단히 정리해서 답하세요."
    )


@app.post("/api/chat", response_model=ApiChatResponse)
def api_chat(request: ApiChatRequest):
    if request.festival_id is not None and request.category:
        # 3단계: 축제 앵커 + 카테고리 → 거리순 추천
        anchor = services.get_place(request.festival_id)
        if not anchor:
            raise HTTPException(status_code=404, detail="선택한 축제를 찾을 수 없습니다.")
        scored = services.nearby_by_category_from_anchor(anchor, request.category)
        places = [p for p, _ in scored]
        distance_by_id = {p.place_id: d for p, d in scored}
        prompt = build_nearby_prompt(anchor, request.category, scored)
    else:
        # 1단계: 자유 텍스트 → 축제 후보 검색 (지역은 키워드 검색이, 동행 힌트는 재정렬이 이미 반영)
        places = services.search_festivals_for_chat(request.question, lat=request.lat, lon=request.lon)
        distance_by_id = {}
        companion_hint = services.detect_companion_hint(request.question)
        prompt = build_festival_prompt(request.question, places, companion_hint)

    messages = [{"role": "system", "content": "서울 축제/여행 안내 챗봇입니다."}]
    for turn in request.history[-6:]:  # 최근 6턴만 컨텍스트로 사용(토큰 비용 제어)
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": prompt})

    try:
        answer = openai_client.chat_completion(messages=messages)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    sources = [
        ChatSourceOut(
            id=p.place_id, title=p.title, address=p.address1, tel=p.tel,
            category=p.content_type_id, distance_km=distance_by_id.get(p.place_id),
        )
        for p in places
    ]
    return ApiChatResponse(answer=answer, sources=sources)
```

`from app import services` import 추가 필요(서비스 함수를 `services.xxx`로 호출). `sources`가 비어도 기존 `/chat`처럼 404를 던지지 않고 "찾지 못했습니다" 안내 답변을 생성하도록 완화한다(사용자가 일반 대화를 시도할 때 UX가 막히지 않도록). `festival_id`+`category`가 함께 오지 않으면 무조건 1단계(축제 검색)로 처리하므로, 프론트가 상태를 잘못 관리해도 최소한 축제 추천으로는 복귀한다(안전한 기본 동작).

### 1-5. 파일 변경 요약

| 파일 | 변경 |
|---|---|
| `backend/app/openai_client.py` | 전면 교체(1.x 클라이언트) |
| `backend/app/services.py` | `_haversine_km`, `_extract_keywords`, `CATEGORY_LABEL_MAP`, `COMPANION_HINT_KEYWORDS`, `detect_companion_hint`, `search_festivals_for_chat`, `get_place`, `nearby_by_category_from_anchor` 추가 |
| `backend/app/main.py` | `ApiChatRequest/Response`, `build_festival_prompt`, `build_nearby_prompt`, `POST /api/chat` 추가 |
| `backend/requirements.txt` | 변경 없음(`openai>=1.0.0`이 이미 맞음) |

### 1-6. 검증 방법

```powershell
cd backend
$env:OPENAI_API_KEY="sk-..."
python run_server.py
# 1단계: 축제 검색(지역 키워드만)
curl -X POST http://127.0.0.1:8001/api/chat -H "Content-Type: application/json" -d '{"question":"불꽃축제 알려줘"}'
# 1단계: 지역 + 동행 힌트가 섞인 자유 텍스트 — 강남 지역 매칭 + 가족 힌트 재정렬이 함께 동작하는지 확인
curl -X POST http://127.0.0.1:8001/api/chat -H "Content-Type: application/json" -d '{"question":"강남 근처에서 가족이랑 갈만한 축제 추천해줘"}'
# 3단계: 위 응답의 sources[0].id 를 festival_id로 사용해 주변 숙박 거리순 조회
curl -X POST http://127.0.0.1:8001/api/chat -H "Content-Type: application/json" -d '{"question":"주변 숙박 추천해줘","festival_id":2556687,"category":"숙박"}'
```
1단계 응답의 `sources`는 `distance_km`가 없고(`null`), 3단계 응답의 `sources`는 `distance_km` 오름차순으로 정렬되어 있는지 확인. 두 번째 curl은 "강남"이 포함된 주소의 축제가 우선 노출되고, 제목에 "가족/키즈/패밀리" 등이 포함된 축제가 있다면 그 축제가 앞쪽에 오는지 확인(둘 다 없어도 에러 없이 기본 후보가 나와야 함 — 휴리스틱이므로 매칭 실패가 정상 동작임). `OPENAI_API_KEY` 미설정 시 500 에러(레거시처럼 404 아님) 확인.

---

## 2. 익명 게시판 (내장 라이브러리 기반 비밀번호 CRUD) — ⏸ 보류 (다른 팀원 담당)

> **상태: 이번 8시간 실행 범위에서 제외.** 이 섹션은 다른 팀원이 게시판을 구현하기로 결정되어 **실제로 착수하지 않는다.** 아래 내용은 삭제하지 않고 그대로 남겨 두는데, 팀원이 동일한 엔드포인트/스키마 설계(`POST/GET/PUT/DELETE /api/posts`, `PostCreate`/`PostUpdate`/`PostDetailOut` 등)를 그대로 채택하거나 참고할 수 있도록 하기 위함이다. 담당자가 다른 설계를 택하면 이 섹션은 그에 맞춰 다시 갱신한다.
>
> **연동 시 주의할 접점(팀원과 공유 필요)**:
> - `backend/app/main.py`는 맨 끝에 4절의 SPA catch-all 라우트(`@app.get("/{full_path:path}")`)가 추가될 예정이므로, 게시판 라우트는 **반드시 그 이전에** 등록해야 한다.
> - `Base.metadata.create_all(bind=ENGINE)`(2-2절)로 테이블을 추가하면 `import_seoul_data.py`의 파괴적 `ensure_db()`와 경로가 분리되어 기존 축제 데이터가 보존된다 — 게시판 담당자도 이 방식을 그대로 쓰는 것을 권장.
> - 프론트 라우팅(`/board`, `/board/write`, `/board/:postId`)과 `App.vue` 내비게이션 자리를 미리 비워두면(3절 ChatWidget과 무관한 영역이라 충돌 없음) 병합이 수월하다.

### 2-1. 비밀번호 해싱 유틸 — 신규 파일 `backend/app/security.py`

패키지 추가 없이 `hashlib`(해시) + `secrets`(salt 생성) + `hmac`(타이밍 안전 비교) — 전부 표준 라이브러리.

```python
import hashlib
import hmac
import secrets

_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest_hex = stored.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS)
    return hmac.compare_digest(candidate.hex(), digest_hex)
```

> **트레이드오프**: 요구사항은 `hashlib.sha256`을 예시로 들었지만, 단순 `sha256(salt+password)`는 무차별대입에 취약하다. 동일하게 표준 라이브러리 안에서 구현 가능한 `hashlib.pbkdf2_hmac`(반복 해싱, salt 내장 지원)을 쓰면 추가 패키지 없이도 훨씬 안전하다. 8시간 제약상 bcrypt/argon2(추가 설치 필요) 대신 이 방식을 채택 — RFP 자체가 "교육 목적, 평문 저장도 허용"이라 명시한 수준을 상회하는 선택.



### 2-2. DB 모델 — `backend/app/models.py`에 추가

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_name = Column(String, nullable=False, default="익명")
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**테이블 생성 방식**: `import_seoul_data.py`의 `ensure_db()`는 DB 파일을 **통째로 삭제 후 스키마 재생성**하므로 이미 적재된 축제/관광지 데이터가 날아간다 — 게시판 도입을 위해 이 스크립트를 다시 돌리면 안 된다. 대신 SQLAlchemy의 비파괴적 방식을 쓴다.

`backend/app/main.py` 상단(앱 생성 직후)에 추가:

```python
from app.orm import Base, ENGINE
from app import models  # Post/Place 모델이 Base.metadata에 등록되도록 import

Base.metadata.create_all(bind=ENGINE)  # 없는 테이블(posts)만 생성, 기존 테이블은 그대로 둠
```

`create_all`은 이미 존재하는 `places`, `festival_related_places` 테이블은 건드리지 않고 `posts`만 새로 만든다(SQLAlchemy가 `CREATE TABLE IF NOT EXISTS`와 동등하게 동작).

문서화를 위해 `project/seoul_festival_schema.sql`에도 아래 DDL을 참고용으로 덧붙인다(실제 실행 경로는 아니고 스키마 문서 동기화 목적):

```sql
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_name TEXT NOT NULL DEFAULT '익명',
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### 2-3. 스키마 — `backend/app/schemas.py`에 추가

```python
from datetime import datetime


class PostCreate(BaseModel):
    title: str
    content: str
    author_name: str = "익명"
    password: str


class PostUpdate(BaseModel):
    title: str
    content: str
    password: str


class PostDeleteRequest(BaseModel):
    password: str


class PostListItemOut(BaseModel):
    id: int
    title: str
    author_name: str
    created_at: datetime


class PostDetailOut(PostListItemOut):
    content: str
    updated_at: datetime
```

`password`/`password_hash`는 어떤 Out 스키마에도 포함하지 않음 — 응답에 절대 노출 금지.

### 2-4. 서비스 함수 — 신규 파일 `backend/app/post_service.py`

기존 `services.py`가 세션 open/close 패턴을 함수마다 반복하는 스타일을 그대로 따른다(일관성 우선, 대규모 리팩터링은 8시간 범위 밖).

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Post
from app.orm import SessionLocal
from app.security import hash_password, verify_password


def create_post(title: str, content: str, author_name: str, password: str) -> Post:
    db: Session = SessionLocal()
    try:
        post = Post(
            title=title,
            content=content,
            author_name=author_name or "익명",
            password_hash=hash_password(password),
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    finally:
        db.close()


def list_posts(limit: int = 50):
    db: Session = SessionLocal()
    try:
        return db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
    finally:
        db.close()


def get_post_or_404(db: Session, post_id: int) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


def get_post(post_id: int) -> Post:
    db: Session = SessionLocal()
    try:
        return get_post_or_404(db, post_id)
    finally:
        db.close()


def update_post(post_id: int, title: str, content: str, password: str) -> Post:
    db: Session = SessionLocal()
    try:
        post = get_post_or_404(db, post_id)
        if not verify_password(password, post.password_hash):
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        post.title, post.content = title, content
        db.commit()
        db.refresh(post)
        return post
    finally:
        db.close()


def delete_post(post_id: int, password: str) -> None:
    db: Session = SessionLocal()
    try:
        post = get_post_or_404(db, post_id)
        if not verify_password(password, post.password_hash):
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        db.delete(post)
        db.commit()
    finally:
        db.close()
```

### 2-5. API 엔드포인트 — `backend/app/main.py`

```python
from app.schemas import PostCreate, PostUpdate, PostDeleteRequest, PostListItemOut, PostDetailOut
from app import post_service


@app.post("/api/posts", response_model=PostDetailOut, status_code=201)
def create_post_endpoint(body: PostCreate):
    post = post_service.create_post(body.title, body.content, body.author_name, body.password)
    return post


@app.get("/api/posts", response_model=List[PostListItemOut])
def list_posts_endpoint():
    return post_service.list_posts()


@app.get("/api/posts/{post_id}", response_model=PostDetailOut)
def get_post_endpoint(post_id: int):
    return post_service.get_post(post_id)


@app.put("/api/posts/{post_id}", response_model=PostDetailOut)
def update_post_endpoint(post_id: int, body: PostUpdate):
    return post_service.update_post(post_id, body.title, body.content, body.password)


@app.delete("/api/posts/{post_id}", status_code=204)
def delete_post_endpoint(post_id: int, body: PostDeleteRequest):
    post_service.delete_post(post_id, body.password)
```

> **트레이드오프**: REST 관례상 `DELETE`에 바디를 싣는 것이 논쟁적이다(일부 프록시/캐시가 DELETE 바디를 무시). `fetch()`/axios는 문제없이 지원하므로 이번 규모(사내 과제, 단일 포트 배포)에서는 채택. 더 보수적으로 가려면 `POST /api/posts/{id}/delete`로 바꿔도 되지만 시간 대비 이득이 적어 표준 REST 형태를 유지.

### 2-6. 프론트엔드 — Vue 3

**라우터 추가 — `frontend/src/main.js`**
```js
import BoardListPage from './pages/BoardListPage.vue';
import BoardWritePage from './pages/BoardWritePage.vue';
import BoardDetailPage from './pages/BoardDetailPage.vue';

const routes = [
  { path: '/', component: FestivalListPage },
  { path: '/festivals/:festivalId', component: FestivalDetailPage, props: true },
  { path: '/board', component: BoardListPage },
  { path: '/board/write', component: BoardWritePage },
  { path: '/board/:postId', component: BoardDetailPage, props: true },
];
```

**네비게이션 — `frontend/src/App.vue`**: 현재 라우트가 2개뿐이라 이동 수단이 없다. `<header class="hero">` 안에 최소 내비게이션 추가:
```html
<nav class="top-nav">
  <router-link to="/">축제</router-link>
  <router-link to="/board">커뮤니티</router-link>
</nav>
```

**`frontend/src/pages/BoardListPage.vue`** (신규)
```vue
<template>
  <section>
    <div class="board-header">
      <h2 class="page-title">커뮤니티</h2>
      <router-link class="btn-primary" to="/board/write">글쓰기</router-link>
    </div>
    <ul class="board-list">
      <li v-for="post in posts" :key="post.id">
        <router-link :to="`/board/${post.id}`">{{ post.title }}</router-link>
        <span class="board-meta">{{ post.author_name }} · {{ formatDate(post.created_at) }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const posts = ref([]);
const formatDate = (iso) => new Date(iso).toLocaleString('ko-KR');

onMounted(async () => {
  const res = await fetch('/api/posts');
  posts.value = await res.json();
});
</script>
```

**`frontend/src/pages/BoardWritePage.vue`** (신규, 작성/수정 공용)
```vue
<template>
  <section>
    <h2 class="page-title">{{ isEdit ? '글 수정' : '글쓰기' }}</h2>
    <form class="board-form" @submit.prevent="submit">
      <input v-model="form.title" placeholder="제목" required />
      <input v-model="form.author_name" placeholder="작성자명(선택, 기본 익명)" />
      <textarea v-model="form.content" placeholder="내용" rows="10" required />
      <input v-model="form.password" type="password" placeholder="비밀번호(수정/삭제 시 필요)" required />
      <button class="btn-primary" type="submit">{{ isEdit ? '수정 완료' : '등록' }}</button>
    </form>
    <p v-if="error" class="error-text">{{ error }}</p>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const isEdit = !!route.query.editId;
const form = reactive({ title: '', author_name: '', content: '', password: '' });
const error = ref('');

onMounted(async () => {
  if (isEdit) {
    const res = await fetch(`/api/posts/${route.query.editId}`);
    const data = await res.json();
    form.title = data.title;
    form.content = data.content;
  }
});

const submit = async () => {
  error.value = '';
  const url = isEdit ? `/api/posts/${route.query.editId}` : '/api/posts';
  const method = isEdit ? 'PUT' : 'POST';
  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form),
  });
  if (res.status === 403) { error.value = '비밀번호가 일치하지 않습니다.'; return; }
  if (!res.ok) { error.value = '요청 처리에 실패했습니다.'; return; }
  const saved = await res.json();
  router.push(`/board/${saved.id}`);
};
</script>
```

**`frontend/src/components/PasswordModal.vue`** (신규, 수정/삭제 공용 모달)
```vue
<template>
  <div v-if="visible" class="modal-backdrop" @click.self="$emit('cancel')">
    <div class="modal-box">
      <h3>비밀번호 확인</h3>
      <input v-model="pwd" type="password" placeholder="비밀번호를 입력하세요" @keyup.enter="confirm" />
      <div class="modal-actions">
        <button class="btn-primary" @click="confirm">확인</button>
        <button class="btn-secondary" @click="$emit('cancel')">취소</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({ visible: Boolean });
const emit = defineEmits(['confirm', 'cancel']);
const pwd = ref('');

watch(() => props.visible, (v) => { if (!v) pwd.value = ''; });

const confirm = () => emit('confirm', pwd.value);
</script>
```

**`frontend/src/pages/BoardDetailPage.vue`** (신규)
```vue
<template>
  <section>
    <router-link to="/board">← 목록으로</router-link>
    <h2>{{ post.title }}</h2>
    <p class="board-meta">{{ post.author_name }} · {{ formatDate(post.created_at) }}</p>
    <p class="board-content">{{ post.content }}</p>
    <div class="board-actions">
      <button class="btn-primary" @click="pendingAction = 'edit'">수정</button>
      <button class="btn-danger" @click="pendingAction = 'delete'">삭제</button>
    </div>
    <PasswordModal
      :visible="!!pendingAction"
      @cancel="pendingAction = null"
      @confirm="onConfirm"
    />
    <p v-if="error" class="error-text">{{ error }}</p>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import PasswordModal from '../components/PasswordModal.vue';

const props = defineProps({ postId: String });
const route = useRoute();
const router = useRouter();
const post = ref({ title: '', content: '', author_name: '', created_at: new Date().toISOString() });
const pendingAction = ref(null);
const error = ref('');
const formatDate = (iso) => new Date(iso).toLocaleString('ko-KR');

const load = async () => {
  const id = props.postId || route.params.postId;
  const res = await fetch(`/api/posts/${id}`);
  post.value = await res.json();
};

onMounted(load);

const onConfirm = async (password) => {
  const id = props.postId || route.params.postId;
  error.value = '';
  if (pendingAction.value === 'delete') {
    const res = await fetch(`/api/posts/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    });
    if (res.status === 403) { error.value = '비밀번호가 일치하지 않습니다.'; pendingAction.value = null; return; }
    router.push('/board');
  } else {
    router.push(`/board/write?editId=${id}`);
  }
};
</script>
```

**CSS 추가 — `frontend/src/style.css`** (기존 변수/톤 재사용): `.top-nav`, `.board-header`, `.board-list`, `.board-meta`, `.board-form`, `.board-content`, `.board-actions`, `.btn-secondary`, `.btn-danger`, `.error-text`, `.modal-backdrop`, `.modal-box`, `.modal-actions` 클래스를 기존 `--color-*` 변수를 사용해 추가(신규 색상 변수 도입 없이 `var(--color-danger)` 등 기존 값 재사용).

### 2-7. 검증 방법

1. `POST /api/posts`로 글 작성 → 응답에 `password`/`password_hash` 없는지 확인
2. 브라우저에서 `/board` → 목록 → 상세 → 수정(틀린 비번 → 403 확인 → 맞는 비번 → 수정 반영) → 삭제(틀린 비번 실패 → 맞는 비번 성공, 목록에서 사라짐) 전체 플로우 수동 테스트

---

## 3. 챗봇 프론트엔드 UI 연동 (+ 피드백: 축제 우선 추천 → 카테고리 follow-up → 거리순 추천 플로우)

### 3-1. 신규 컴포넌트 `frontend/src/components/ChatWidget.vue`

**(피드백 반영)** 상단에 고정된 필터 칩(페르소나/카테고리)을 두던 이전 설계 대신, **대화 흐름 자체가 3단계 상태 기계**로 진행된다.

1. **`discover`(기본 상태)**: 사용자가 자유 텍스트로 질문하면 `POST /api/chat`(축제 전용 검색, 1-3절 `search_festivals_for_chat`)을 호출하고, 응답의 `sources`(축제 후보)를 해당 말풍선 아래에 **클릭 가능한 칩 목록**으로 붙여서 보여준다.
2. **축제 선택 → `awaiting_category`**: 사용자가 축제 칩 하나를 클릭하면 `selectedFestival`을 저장하고, **백엔드 호출 없이 프론트에서 즉시** "이 축제 주변에 또 어떤 시설이 궁금한가요?"라는 봇 메시지 + 카테고리 칩(관광지/문화시설/레포츠/숙박/쇼핑)을 붙여 보여준다.
3. **카테고리 선택 → 거리순 결과**: 사용자가 카테고리 칩을 클릭하면 `festival_id`(앵커) + `category`로 `POST /api/chat`을 호출(1-3절 `nearby_by_category_from_anchor`)하고, 응답 `sources`(거리 오름차순)를 **말풍선 텍스트 + 별도의 거리순 리스트(카드)** 두 형태로 함께 보여준다(LLM 문장에만 의존하면 정렬이 흐트러져 보일 수 있어, 실제 정렬된 데이터를 그대로 렌더링하는 리스트를 병행한다). 이후 같은 축제에 대해 다른 카테고리를 또 물어볼 수 있도록 카테고리 칩을 다시 노출한다.

```vue
<template>
  <div class="chat-widget">
    <button class="chatbot-floating" aria-label="챗봇 열기" @click="open = !open">💬</button>
    <div v-if="open" class="chat-panel">
      <div class="chat-header">
        <span>축제 여행 챗봇</span>
        <button class="chat-close" @click="open = false">✕</button>
      </div>

      <div class="chat-messages" ref="messagesEl">
        <template v-for="(msg, idx) in messages" :key="idx">
          <div :class="['chat-bubble', msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-bot']">
            {{ msg.content }}
          </div>

          <!-- 1단계 응답: 축제 후보를 칩으로 노출 -->
          <div v-if="msg.festivalOptions?.length" class="chat-chip-row">
            <button
              v-for="f in msg.festivalOptions"
              :key="f.id"
              class="chat-chip"
              @click="selectFestival(f)"
            >{{ f.title }}</button>
          </div>

          <!-- 2단계: 카테고리 follow-up 칩 -->
          <div v-if="msg.categoryPrompt" class="chat-chip-row">
            <button
              v-for="c in categoryOptions"
              :key="c.value"
              class="chat-chip"
              @click="pickCategory(c)"
            >{{ c.label }}</button>
          </div>

          <!-- 3단계 응답: 실제 거리순 정렬 리스트(LLM 문장과 별개로 데이터 그대로 렌더링) -->
          <div v-if="msg.nearbyResults?.length" class="chat-nearby-list">
            <div v-for="p in msg.nearbyResults" :key="p.id" class="chat-nearby-item">
              <strong>{{ p.title }}</strong>
              <span>{{ p.distance_km?.toFixed(1) }}km · {{ p.address || '주소 정보 없음' }}</span>
            </div>
          </div>
        </template>

        <div v-if="loading" class="chat-bubble chat-bubble-bot chat-loading">
          <span></span><span></span><span></span>
        </div>
      </div>

      <form class="chat-input-row" @submit.prevent="sendFreeText">
        <input v-model="draft" placeholder="예: 강남 근처 가족이랑 갈만한 축제" :disabled="loading" />
        <button class="btn-primary" type="submit" :disabled="loading || !draft.trim()">전송</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const open = ref(false);
const draft = ref('');
const loading = ref(false);
const messagesEl = ref(null);

const messages = ref([
  { role: 'assistant', content: '안녕하세요! 관심 있는 축제를 말씀해주세요. 지역이나 누구와 갈지도 함께 말씀해주시면 더 잘 골라드려요. (예: "강남 근처 가족이랑 갈만한 축제 추천해줘")' },
]);

const selectedFestival = ref(null); // { id, title }

const categoryOptions = [
  { label: '관광지', value: '관광지' },
  { label: '문화시설', value: '문화시설' },
  { label: '레포츠', value: '레포츠' },
  { label: '숙박', value: '숙박' },
  { label: '쇼핑', value: '쇼핑' },
];

const scrollToBottom = async () => {
  await nextTick();
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
};

const callChatApi = async (payload) => {
  const history = messages.value.map(({ role, content }) => ({ role, content }));
  return fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, history }),
  });
};

// 1단계: 자유 텍스트 → 축제 후보 탐색
const sendFreeText = async () => {
  const question = draft.value.trim();
  if (!question) return;
  messages.value.push({ role: 'user', content: question });
  draft.value = '';
  loading.value = true;
  scrollToBottom();
  try {
    const res = await callChatApi({ question });
    const data = await res.json();
    messages.value.push({
      role: 'assistant',
      content: res.ok ? data.answer : '죄송해요, 답변을 가져오지 못했어요.',
      festivalOptions: res.ok ? data.sources : [],
    });
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '네트워크 오류가 발생했어요.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

// 2단계: 축제 선택 → 카테고리 follow-up (백엔드 호출 없이 즉시 안내)
const selectFestival = (festival) => {
  selectedFestival.value = festival;
  messages.value.push({ role: 'user', content: `"${festival.title}" 축제를 선택했어요.` });
  messages.value.push({
    role: 'assistant',
    content: `좋아요! "${festival.title}" 주변에 또 어떤 시설이 궁금하세요?`,
    categoryPrompt: true,
  });
  scrollToBottom();
};

// 3단계: 카테고리 선택 → festival_id 앵커 기준 거리순 추천
const pickCategory = async (category) => {
  if (!selectedFestival.value) return;
  messages.value.push({ role: 'user', content: `${category.label} 추천해줘` });
  loading.value = true;
  scrollToBottom();
  try {
    const res = await callChatApi({
      question: `${selectedFestival.value.title} 주변 ${category.label} 추천해줘`,
      festival_id: selectedFestival.value.id,
      category: category.value,
    });
    const data = await res.json();
    messages.value.push({
      role: 'assistant',
      content: res.ok ? data.answer : '죄송해요, 답변을 가져오지 못했어요.',
      nearbyResults: res.ok ? data.sources : [],
      categoryPrompt: res.ok, // 같은 축제로 다른 카테고리를 이어서 물어볼 수 있도록 칩을 다시 노출
    });
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '네트워크 오류가 발생했어요.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};
</script>
```

`App.vue`에서 교체:
```html
<!-- 기존: <button class="chatbot-floating" ...>💬</button> -->
<ChatWidget />
```
```js
import ChatWidget from './components/ChatWidget.vue';
```

### 3-2. CSS 추가(`style.css`)

`.chat-widget`(fixed 컨테이너), `.chat-panel`(320×460px 카드, `position: fixed; right:28px; bottom:104px;`), `.chat-header`, `.chat-messages`(`overflow-y:auto`, `max-height`), `.chat-chip-row`(말풍선 바로 아래 붙는 칩 그룹, `display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 12px;`), `.chat-chip`(pill 버튼, `background:#F1F5F9`, hover 시 `background:var(--color-primary); color:white;`), `.chat-nearby-list`(거리순 결과 카드 목록, `display:grid; gap:8px; margin:6px 0 12px;`), `.chat-nearby-item`(`display:flex; justify-content:space-between; background:#F8FAFC; border-radius:12px; padding:8px 12px; font-size:13px;`), `.chat-bubble-user`(우측 정렬, `--color-primary` 배경), `.chat-bubble-bot`(좌측 정렬, 회색 배경), `.chat-loading span`(점 3개 bounce 애니메이션 `@keyframes`), `.chat-input-row`(`display:flex`). 모바일 대응은 `@media (max-width:768px)`에서 `.chat-panel { width: 100vw; height: 70vh; right:0; bottom:0; border-radius:20px 20px 0 0; }`로 풀스크린에 가깝게 전환(RFP의 "모바일 대응, 플로팅 UI" 요구 충족). 칩 행은 좁은 화면에서 `flex-wrap`으로 자동 줄바꿈되므로 별도 모바일 전용 스타일은 불필요.

### 3-3. 로딩 인디케이터 / 자동 스크롤 / 3단계 플로우 구현 포인트

- **로딩**: `loading` ref로 전송 버튼 비활성화 + 말풍선 자리에 점 3개 bounce 애니메이션(추가 라이브러리 불필요, 순수 CSS `@keyframes`).
- **자동 스크롤**: 메시지 배열이 바뀔 때마다 `nextTick()` 이후 `messagesEl.scrollTop = messagesEl.scrollHeight` — Vue가 DOM을 갱신한 다음 프레임에 스크롤해야 최신 높이를 기준으로 계산되므로 `nextTick` 필수(이 부분을 빼먹으면 한 메시지씩 밀려서 스크롤되는 흔한 버그가 남).
- **대화 히스토리**: 클라이언트 상태(`messages` ref)에만 보관하는 세션 한정 히스토리로 충분(요구사항은 "대화 히스토리 유지"이지 서버 영속화가 아님, 새로고침 시 초기화되는 것은 8시간 범위에서 합리적 트레이드오프).
- **2단계가 API 호출 없이 즉시 반응하는 이유**: "이 축제 주변에 또 어떤 시설이 궁금한가요?"라는 follow-up 질문 자체는 고정 문구이고 OpenAI가 판단할 내용이 없어, 왕복 지연(latency)과 토큰 비용을 아낄 수 있는 곳에서는 굳이 LLM을 거치지 않는다 — 실제 데이터 조회(3단계)에서만 백엔드를 호출한다.
- **거리순 리스트를 LLM 문장과 별도로 렌더링하는 이유**: "거리 순으로 추천"이 요구사항의 핵심인데, LLM이 프롬프트에 이미 정렬된 목록을 받아도 문장으로 재서술하는 과정에서 순서를 흐트러뜨리거나 일부를 누락할 위험이 있다. `nearbyResults`를 서버가 계산한 `distance_km` 순서 그대로 별도 카드 리스트로 보여줘서, 실제 정렬 결과를 사용자가 신뢰할 수 있게 한다.
- **같은 축제에서 카테고리를 반복 선택**: `pickCategory` 응답에도 `categoryPrompt: true`를 다시 심어 카테고리 칩을 재노출하므로, 사용자는 같은 축제를 앵커로 숙박→쇼핑처럼 여러 카테고리를 이어서 물어볼 수 있다. 다른 축제로 넘어가려면 자유 텍스트로 다시 질문하면 된다(별도의 "축제 다시 찾기" 버튼은 8시간 범위에서 생략 — 6절 축소 전략 참고).

---

## 4. 단일 포트 배포 — FastAPI가 Vue 빌드 산출물 서빙

### 4-1. 빌드

```powershell
cd frontend
npm run build   # → frontend/dist/ 생성 (vite.config.js에 outDir 미지정 → 기본값 dist)
```

### 4-2. `backend/app/main.py` 최하단에 정적 서빙 + SPA 폴백 추가

**반드시 파일 맨 끝, 다른 모든 `/api/...` 라우트 정의 이후**에 추가해야 한다(FastAPI는 등록 순서대로 라우트를 매칭하므로, catch-all이 먼저 있으면 API 요청까지 가로챈다).

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
```

**왜 `StaticFiles(html=True)`를 루트에 바로 mount하지 않는가**: Starlette의 `StaticFiles(html=True)`는 존재하지 않는 서브경로(`/board/5` 같은 Vue Router 히스토리 모드 경로)에 대해 자동으로 `index.html`로 폴백해주지 않고 404를 반환한다. 위처럼 **명시적 catch-all 라우트**를 커스텀으로 만들어야 "실제 정적 파일이면 그 파일을, 아니면 index.html을 반환"하는 SPA 폴백이 정확히 동작한다. `/assets`(vite가 생성하는 JS/CSS 청크 경로)만 별도로 `StaticFiles`에 mount해 정적 파일 서빙 성능/캐싱 헤더 이점을 유지한다.

### 4-3. `backend/run_server.py` — 변경 불필요

이미 `PORT` 환경변수를 읽어 `uvicorn.run("app.main:app", host="127.0.0.1", port=port)`로 구동한다. Render 배포 시 `host="0.0.0.0"`로 바꿔야 외부 접속이 가능하므로 아래처럼 1줄만 수정:

```python
uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
```

### 4-4. 로컬 개발 vs 프로덕션 단일 포트 — 두 흐름 모두 유지

| 모드 | 실행 방법 | 포트 구성 |
|---|---|---|
| 개발(핫리로드) | `frontend`: `npm run dev` / `backend`: `python run_server.py` | 5173(FE, `/api`→8001 프록시) + 8001(BE) — 지금과 동일하게 유지 |
| 프로덕션(단일 포트) | `npm run build` → `python run_server.py` | 8001 하나로 API + 정적 페이지 모두 서빙 |

개발 편의성을 유지하면서 배포 요구사항(단일 포트)도 만족시키는 방식 — `vite.config.js`는 변경하지 않는다.

### 4-5. Render 배포 설정 (참고, 8시간 내 실제 배포까지는 시간 여유에 따라 선택)

Render의 "Build Command"/"Start Command"에 아래를 등록(레포 루트 기준):
```
Build Command: cd frontend && npm install && npm run build
Start Command: cd backend && pip install -r requirements.txt && python run_server.py
```
환경변수 탭에 `OPENAI_API_KEY` 등록(코드/레포에는 절대 기재 안 함 — RFP 제약 그대로 준수).

> **트레이드오프**: RFP는 원래 "프론트 Netlify / 백엔드 Render" 분리 배포를 요구하지만, 이번 요구사항 4번은 명시적으로 "단일 포트로 전체 서비스 구동"을 요청했다. 두 요구가 상충하므로, **8시간 데드라인 안에서는 단일 포트(Render 1개)로 통합 배포**하는 쪽을 권장하고, 시간이 남으면 Netlify에 프론트만 별도로도 배포해 두 요구를 모두 만족시키는 것을 스트레치 목표로 남긴다.

### 4-6. 검증 방법

```powershell
cd frontend; npm run build
cd ../backend; python run_server.py
```
브라우저에서 `http://127.0.0.1:8001/` (목록), `http://127.0.0.1:8001/board`, `http://127.0.0.1:8001/festivals/2556687` 등 새로고침 시에도(딥링크 직접 접근) 정상 렌더링되는지 확인 — SPA 폴백이 안 되면 새로고침 시 404가 뜨므로 이게 핵심 체크포인트.

---

## 5. 전체 변경/신규 파일 목록

**백엔드 — 이번 8시간 범위에서 실행**
- 수정: `backend/app/openai_client.py`, `backend/app/main.py`(`/api/chat` 및 4절 SPA catch-all), `backend/app/services.py`(축제 검색 + 축제앵커 기반 카테고리별 거리순 조회), `backend/run_server.py`(host만)

**프론트엔드 — 이번 8시간 범위에서 실행**
- 수정: `frontend/src/App.vue`(ChatWidget 교체), `frontend/src/style.css`(챗봇 패널/칩 클래스 추가)
- 신규: `frontend/src/components/ChatWidget.vue`

**⏸ 보류 (다른 팀원 담당 — 계획만 보관, 이번 실행 범위 아님)**
- 백엔드 수정: `backend/app/models.py`(`Post`), `backend/app/schemas.py`(`Post*`), `project/seoul_festival_schema.sql`(문서용 DDL)
- 백엔드 신규: `backend/app/security.py`, `backend/app/post_service.py`
- 프론트 수정: `frontend/src/main.js`(게시판 라우트), `frontend/src/App.vue`(nav 링크)
- 프론트 신규: `frontend/src/pages/BoardListPage.vue`, `frontend/src/pages/BoardWritePage.vue`, `frontend/src/pages/BoardDetailPage.vue`, `frontend/src/components/PasswordModal.vue`

**문서**
- `research.md`(기존, 참고용) / 이 `plan.md`

---

## 6. 리스크 및 시간 초과 시 축소 전략

0. **게시판(2절)은 이미 스코프 아웃** — 다른 팀원 담당이므로 시간 배분 대상에서 아예 제외. 단, 팀원 작업물과 병합 시 main.py 라우트 순서(게시판 라우트가 4절 SPA catch-all보다 먼저 와야 함)만 조율하면 된다.
1. **가장 먼저 포기 가능한 것**: 4절(단일 포트) → 시간이 부족하면 기존처럼 FE(5173)/BE(8001) 분리 구동 상태로 제출하고 배포 URL만 각각 제공(원래 RFP 요구사항과도 부합하므로 오히려 안전한 폴백).
2. **두 번째로 포기 가능한 것**: 3단계 흐름 중 "같은 축제에서 카테고리 반복 선택"(3-3절, 카테고리 칩 재노출), 히스토리 멀티턴 컨텍스트 전달(3-1의 `history`), 1단계의 동행 힌트 재정렬(`detect_companion_hint`) → 실패 시 카테고리 선택은 1회성으로, 히스토리는 매번 새 대화로, 동행 힌트는 재정렬 없이 원래 순서 그대로 축소 가능(각각 독립적인 보강 로직이라 하나씩 꺼도 나머지 플로우에 영향 없음). 지역 반영(title/address1 키워드 검색)은 애초에 기존 검색 로직 자체이므로 별도로 뺄 것이 없다.
3. **절대 포기 불가**: 1절(OpenAI 마이그레이션) — 현재 상태로는 챗봇이 아예 크래시하므로 최우선 고정. 마찬가지로 "축제 우선 추천 → 카테고리 follow-up → 거리순 추천" 플로우(피드백 3번 핵심 요구사항)도 최소 골격(1단계 축제 검색 + 2단계 카테고리 질문 + 3단계 거리순 결과)만은 반드시 남긴다.

---

## 7. 최종 TODO 리스트 (8시간, 의존성 순 배치)

> 게시판(CRUD)은 다른 팀원 담당으로 계속 보류하기로 확정했으므로(6절 0번), 아래 TODO에는 게시판 관련 작업(비밀번호 해싱 API `security.py` 포함 — 해당 API는 게시판 전용이라 게시판이 빠지면 존재 이유가 없음)을 넣지 않았다. 순서는 실제 의존 관계를 반영한다 — 뒤 단계는 앞 단계 산출물이 있어야 검증 가능하므로, 병렬로 착수하더라도 이 순서대로 "완료 확인"까지는 마치고 넘어가는 것을 권장한다.

### 0. 준비 (0:00–0:20)
- [x] `project/seoul_festival.db` 존재 및 `places` 테이블에 서울 데이터(6개 카테고리)가 적재되어 있는지 확인
- [x] `OPENAI_API_KEY`를 `.env` 또는 환경변수로 로컬에 설정(커밋 금지 재확인) — *로컬에 실제 키는 미설정 상태로 진행, 500 에러 경로로 검증(아래 4절 참고)*
- [x] `backend/requirements.txt`의 `openai>=1.0.0`이 실제 설치된 버전과 맞는지 `pip show openai`로 확인 — 설치된 버전 `openai 2.45.0`

### 1. 백엔드 — OpenAI 마이그레이션 (0:20–1:00, plan.md 1-2절)
- [x] `backend/app/openai_client.py`를 `from openai import OpenAI` 기반 1.x 클라이언트로 전면 교체
- [x] `OpenAIClient.chat_completion`이 `client.chat.completions.create(...)` / `response.choices[0].message.content`로 동작하는지 단독 스모크 테스트(임시 스크립트나 REPL에서 최소 호출) — 키 미설정 시 `RuntimeError` 정상 발생 확인

### 2. 백엔드 — RAG 검색 파이프라인 (1:00–2:00, plan.md 1-3절)
- [x] `backend/app/services.py`에 `_haversine_km`, `_extract_keywords` 추가
- [x] `CATEGORY_LABEL_MAP`, `COMPANION_HINT_KEYWORDS`, `detect_companion_hint` 추가
- [x] `search_festivals_for_chat`(1단계: 축제 키워드/지역 검색 + 동행 힌트 재정렬 + 위치 정렬) 구현
- [x] `get_place`, `nearby_by_category_from_anchor`(3단계: 축제 앵커 기준 카테고리별 거리순 조회) 구현
- [x] 위 함수들을 Python 콘솔/임시 스크립트에서 직접 호출해 반환값(정렬 순서, 빈 결과 처리) 확인 — API 계층 없이 서비스 레이어 단독 검증

### 3. 백엔드 — `/api/chat` 엔드포인트 (2:00–2:30, plan.md 1-4절)
- [x] `backend/app/main.py`에 `ChatMessage`, `ApiChatRequest`(`festival_id`/`category` 포함), `ChatSourceOut`(`distance_km` 포함), `ApiChatResponse` 스키마 추가
- [x] `build_festival_prompt`(1단계, `companion_hint` 파라미터 포함), `build_nearby_prompt`(3단계) 작성
- [x] `POST /api/chat`에서 `festival_id`+`category` 유무로 1단계/3단계 분기하는 라우팅 로직 구현
- [x] `from app import services` 등 필요한 import 정리, `openai_client`/`data_store` 등 기존 전역 객체와 이름 충돌 없는지 확인
- [x] *(부수 발견)* `DATA_ROOT` 경로 계산이 한 단계 부족해 서버 기동 자체가 실패하던 기존 버그를 발견해 함께 수정(`parent.parent` → `parent.parent.parent`)

### 4. 백엔드 검증 (2:30–2:50, plan.md 1-6절)
- [x] 로컬 서버 기동 후 curl로 1단계 호출(`{"question":"불꽃축제 알려줘"}`) → `sources`에 `distance_km`가 없는지 확인
- [x] curl로 지역+동행 힌트 혼합 질문(`"강남 근처에서 가족이랑 갈만한 축제 추천해줘"`) → 주소 매칭/제목 재정렬이 동작하는지 확인 — "강남대로" 주소 매칭 확인(제목에 "가족" 계열 단어가 있는 후보는 없어 재정렬은 무변화, 설계된 정상 동작)
- [x] 1단계 응답의 `sources[0].id`를 `festival_id`로 사용해 3단계 curl(`{"festival_id":...,"category":"숙박"}`) 호출 → `distance_km` 오름차순 정렬 확인 — `TestClient`로 OpenAI 호출만 모킹해 왕복 검증, `[1.33, 2.05, 2.53, 2.75, 2.96]` 오름차순 확인
- [x] `OPENAI_API_KEY` 임시 제거 후 500 에러(404 아님) 나는지 확인, 키 복구 — 로컬 환경에 원래 키가 없어 기본 상태로 500 확인(실제 키를 이용한 정상 답변 왕복은 사용자 환경에서 `OPENAI_API_KEY` 설정 후 추가 확인 필요)

### 5. 프론트엔드 — `ChatWidget.vue` 컴포넌트 (2:50–4:20, plan.md 3-1절)
- [x] `frontend/src/components/ChatWidget.vue` 신규 생성 — 템플릿(말풍선 + 축제 후보 칩 + 카테고리 칩 + 거리순 리스트 + 로딩 인디케이터 + 입력 폼)
- [x] `sendFreeText`(1단계 API 호출), `selectFestival`(2단계, API 호출 없이 즉시 처리), `pickCategory`(3단계 API 호출) 로직 구현
- [x] `scrollToBottom`(`nextTick` 기반 자동 스크롤)을 메시지 추가/로딩 시작·종료 시점마다 호출하도록 연결
- [x] 로딩 중 전송 버튼 비활성화 + bounce 점 3개 애니메이션 표시 확인 — CSS `@keyframes chat-bounce` 및 `:disabled` 스타일로 구현(코드 리뷰로 확인)

### 6. 프론트엔드 — 통합 및 스타일 (4:20–4:50, plan.md 3-2절)
- [x] `frontend/src/App.vue`에서 기존 장식용 `<button class="chatbot-floating">`를 `<ChatWidget />`로 교체
- [x] `frontend/src/style.css`에 `.chat-widget`, `.chat-panel`, `.chat-header`, `.chat-messages`, `.chat-chip-row`, `.chat-chip`, `.chat-nearby-list`, `.chat-nearby-item`, `.chat-bubble-user/-bot`, `.chat-loading`, `.chat-input-row` 및 모바일 미디어쿼리 추가

### 7. 프론트엔드 검증 (4:50–5:10)
- [x] *(자동 검증으로 대체)* `npm run dev` 기동 후 Vite가 `ChatWidget.vue`/`App.vue`를 오류 없이 트랜스폼하는지, `/api` 프록시가 백엔드(`/api/health`)까지 정상 응답하는지 curl로 확인. **주의**: 이 세션에는 실제 브라우저를 조작할 도구가 없어 "칩 클릭 → 답변 표시" 등 시각적 클릭 플로우는 사람이 직접 눈으로 확인하지 못했다 — 로직 자체는 4절에서 백엔드 단독으로, 컴포넌트 문법은 Vite 트랜스폼 성공으로 검증했지만 **사용자가 브라우저로 한 번 더 클릭 확인하는 것을 권장**한다.
- [ ] 대화 중 새 메시지가 추가될 때마다 스크롤이 자동으로 최하단까지 내려가는지 확인 — 코드상 `nextTick` 이후 스크롤 로직은 구현했으나, 실제 렌더링에서의 시각적 확인은 브라우저 도구 부재로 미수행(사용자 확인 필요)
- [ ] 브라우저 폭을 모바일 크기로 줄여 `.chat-panel` 풀스크린 전환 확인 — 미디어쿼리는 작성했으나 실제 화면 확인은 브라우저 도구 부재로 미수행(사용자 확인 필요)

### 8. 배포 — 단일 포트 서빙 (5:10–6:00, plan.md 4절)
- [x] `cd frontend && npm run build`로 `frontend/dist` 생성 확인
- [x] `backend/app/main.py` **맨 끝**(모든 `/api/...` 라우트 등록 이후)에 `/assets` `StaticFiles` mount + SPA catch-all(`@app.get("/{full_path:path}")`) 추가
- [x] `backend/run_server.py`의 `uvicorn.run(...)` host를 `"0.0.0.0"`으로 변경
- [x] *(부수 발견/수정)* Windows 환경의 `mimetypes` 레지스트리가 `.js`를 `text/plain`으로 잘못 인식해 `StaticFiles`가 잘못된 MIME 타입을 내려주는 문제를 발견 — `mimetypes.add_type("application/javascript", ".js")`(+ `.css`)로 명시 등록해 수정. 이 문제를 못 고쳤다면 브라우저가 모듈 스크립트 실행을 거부해 단일 포트 배포 자체가 깨졌을 것.

### 9. 배포 검증 (6:00–6:20, plan.md 4-6절)
- [x] `python run_server.py` 단일 프로세스로 기동 후 `http://127.0.0.1:8001/`에서 목록·상세·챗봇이 모두 동작하는지 확인 — HTTP 200으로 `index.html` 서빙, `/assets/*.js`는 `application/javascript`, `/assets/*.css`는 `text/css`로 정확히 응답
- [x] `http://127.0.0.1:8001/festivals/{id}` 같은 딥링크를 새로고침했을 때 404 없이 정상 렌더링되는지 확인(SPA 폴백 핵심 체크포인트) — 200으로 `index.html` 반환 확인
- [x] `/api/chat` 등 API 요청이 catch-all에 가로채이지 않고 정상 응답하는지 확인 — `/api/health`, `/api/festivals`, `/api/festivals/{id}`, `/api/festivals/{id}/nearby`, `/api/chat` 전부 catch-all보다 우선 매칭됨을 확인

### 10. 마무리 (6:20–8:00)
- [x] 전체 회귀 테스트: 기존 `/api/festivals`, `/api/festivals/{id}`, `/api/festivals/{id}/nearby` 축제 목록/상세 화면이 이번 변경으로 깨지지 않았는지 재확인 — 모두 정상 200 응답, 레거시 JSON 기반 `/health`·`/festivals` 등도 정상(이전에는 `DATA_ROOT` 버그로 서버 기동 자체가 실패했었는데, 이번 수정으로 오히려 함께 고쳐짐)
- [x] README 또는 실행 가이드에 "단일 포트로 빌드+구동" 절차(8절 커맨드) 반영 — 루트 `README.md`에 "Chatbot API"/"Single-port production build" 섹션 추가
- [x] 게시판 담당 팀원에게 병합 시 주의점(2절 상단 노트 — 라우트 등록 순서, `Base.metadata.create_all` 비파괴적 방식) 공유 — plan.md 2절에 이미 문서화되어 있어 팀원 공유용 자료로 그대로 활용 가능(실제 전달은 팀 커뮤니케이션 채널에서 사용자가 진행)
- [x] 최종 커밋 전 `.env`/API 키가 스테이징에 포함되지 않았는지 `git status`/`git diff` 확인 — `.env` 파일 자체가 생성되지 않았고, `git status`에 민감 정보 파일 없음 확인. `frontend/dist`, `node_modules`는 기존 `.gitignore` 규칙(`dist/`, `node_modules/`)으로 이미 제외됨

---

> ✅ **위 피드백(1단계에서 지역/동행 힌트 반영)은 본문(상단 변경 이력 4번, 1-3절 `detect_companion_hint`/트레이드오프, 1-4절 `build_festival_prompt`/`api_chat`, 1-6절 검증 curl, 3-1절 안내 문구, 6절 축소 전략)에 모두 반영 완료.** 