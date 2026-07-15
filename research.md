# ai_project 리서치 보고서

조사일: 2026-07-15 · 브랜치: `feature/chatbot` (origin과 동기화, `backend/app/main.py`에 미스테이징 변경 1건 존재)

---

## 1. 프로젝트 정체

`READE.md`(원문 그대로 오탈자 파일명)에 요약된 SSAFY 팀 프로젝트 개발 의뢰서(RFP) 기반 과제다.

- **이름/컨셉**: LocalHub — 공공데이터(TourAPI 4.0) 기반 "익명 지역 커뮤니티 + 챗봇"
- **필수 스택**: Vue.js 3 (SPA) + FastAPI + SQLite(SQLAlchemy ORM), 배포는 Netlify(FE)/Render(BE)
- **필수 기능**: ① 회원가입 없는 익명 게시판(글 작성 시 수정용 비밀번호 평문 등록/대조), ② 선택한 1개 권역의 CRUD API+화면, ③ `POST /api/chat` 자연어 챗봇, ④ 모바일 대응 플로팅 채팅 UI
- **제약**: 제공 JSON 데이터만 사용(직접 공공API 호출 금지), 커뮤니티 데이터는 반드시 DB 저장, 민감정보는 `.env`로만 관리, **"Claude Code, Codex, Cursor, Antigravity 등 기타 AI 코딩 도구 사용 금지"** (VSCode Copilot + OpenAI API만 허용)
- **납기**: 2026-07-16 15:00 (조사일 기준 익일)

> ⚠️ **주의**: 이 저장소의 `READE.md`는 RFP가 명시적으로 Claude Code 등 외부 AI 코딩 도구 사용을 금지하고 있음을 스스로 기록하고 있다. 현재 이 리서치 자체가 Claude Code로 수행되고 있으므로, 실제 구현 작업 진행 전 사용자는 이 정책 충돌을 인지하고 팀/계약 조건과 재확인할 필요가 있다.

---

## 2. 저장소 구조 개요

```
ai_project/
├── READE.md                 # RFP 요약(팀 자체 분석 문서)
├── AGENTS.md                # Copilot용 "스킬 기반 워크플로우" 안내서
├── .github/copilot-instructions.md  # 위와 동일 취지, gstack 스타일 참조
├── .agents/skills/          # spec/autoplan/review/qa/docs/... 등 Copilot 참고용 스킬 문서 모음(수십 개)
├── 02_3일차_팀프로젝트_개발 의뢰서_전공.pdf   # 원본 RFP PDF
├── analysis_for_excel.tsv   # RFP 요구사항 표 (엑셀 붙여넣기용)
├── data/                    # 5개 권역별 TourAPI JSON 원본 + SCHEMA.md/SOURCE.md
│   ├── 서울/  부산/  대전_충청권/  구미_경북권/  광주_전라권/
├── backend/                 # "정식" 백엔드 (SQLAlchemy ORM, app 패키지)
│   ├── run_server.py
│   ├── requirements.txt
│   └── app/{main,models,schemas,services,orm,database,data_loader,openai_client,import_seoul_data}.py
├── frontend/                # Vue 3 + Vite SPA
│   └── src/{App.vue, main.js, pages/*, components/*}
└── project/                 # 구버전 프로토타입 백엔드(스크립트 스타일) + .venv + seoul_festival.db
```

`.agents/`, `AGENTS.md`, `.github/copilot-instructions.md`는 실제 애플리케이션 로직과 무관한, **VSCode Copilot 에이전트에게 "gstack" 스타일 스킬 워크플로우(spec→plan→review→qa 등)를 따르게 하는 메타 설정**이다. RFP의 "허용 도구는 Copilot"이라는 제약과 일치한다.

---

## 3. 데이터 레이어

- 출처: 한국관광공사 TourAPI 4.0, 공공누리 **제3유형**(출처표시+변경금지, 상업이용/재배포 허용)
- 5개 권역(서울/부산/대전_충청권/구미_경북권/광주_전라권) 각각 관광지/레포츠/문화시설/쇼핑/숙박/여행코스/음식점/축제공연행사 JSON 파일 + `SCHEMA.md`(필드 정의) + `SOURCE.md`(출처/건수/라이선스) 보유
- 최상위 구조: `{region, contentType, contentTypeId, total, items[]}` — `contentTypeId`: 12=관광지, 14=문화시설, 15=축제공연행사, 25=여행코스, 28=레포츠, 32=숙박, 38=쇼핑, 39=음식점
- `mapx`/`mapy`는 JSON 원본에는 **문자열**로 들어있어 사용 시 float 변환 필요(코드에서 실제로 처리함)
- **현재 백엔드는 서울 데이터만 로드**한다(`DATA_ROOT`가 `data/서울`로 하드코딩). 나머지 4개 권역 JSON은 아직 어디에서도 참조되지 않음 — RFP는 "1개 권역 선택"을 요구하므로 서울로 확정된 것으로 보이나, 다른 4개 권역 데이터가 왜 함께 제공되었는지(선택지였는지) 확인 필요.

---

## 4. 백엔드 — 두 개의 병렬 구현이 공존

같은 저장소 안에 **세대가 다른 백엔드 두 벌**이 존재하며 서로 다른 방식으로 같은 SQLite 파일(`project/seoul_festival.db`)과 JSON 데이터를 사용한다.

### 4-1. `project/` — 초기 프로토타입
- `main.py`(스크립트 스타일, `from data_loader import ...`), `.venv` 포함, `seoul_festival_schema.sql`, `seoul_festival.db`, `test_page.html`
- `ARCHITECTURE.md`가 이 폴더의 구조를 문서화(한국어) — 데이터 흐름을 아래처럼 설명:
  1. 서버 기동 시 `SeoulDataStore`가 `data/서울`의 JSON을 전부 메모리에 로드
  2. 요청이 오면 `data_store` 메서드 호출(검색/거리계산/추천)
  3. `/chat`은 검색 결과+질문을 합쳐 OpenAI로 전달
- 실행법: `cd project && uvicorn main:app --reload --port 8000`
- `import_seoul_data.py` (backend에도 동일 파일 존재)가 JSON → SQLite로 1회성 적재하며, `festival_related_places` 테이블에 "축제-주변장소" 관계를 위도/경도 단순 절대값합 정렬로 미리 계산해 저장(진짜 haversine이 아님, `ABS(lat)+ABS(lon)` 근사).

### 4-2. `backend/app/` — 정식(패키지) 구현
- `app.main`이 FastAPI 엔트리포인트. `run_server.py`가 `uvicorn.run("app.main:app", port=8001)`로 구동(기본 8001).
- **API 표면이 이원화되어 있음**:
  - **SQLite/ORM 경로** (`/api/festivals`, `/api/festivals/{id}`, `/api/festivals/{id}/nearby`): `services.py`가 SQLAlchemy `Place` 모델(`models.py`)로 `project/seoul_festival.db`를 직접 쿼리. `content_type_id==15`가 "축제"로 하드코딩. `nearby`는 위경도 유클리드 거리 제곱합(`ORDER BY (Δlat²+Δlon²)`)으로 근사 정렬 — 실제 km 단위 haversine 아님.
  - **JSON 인메모리 경로** (`/health`, `/festivals`, `/nearby`, `/itinerary`, `/persona-recommend`, `/chat`): `data_loader.SeoulDataStore`가 서버 기동 시 `data/서울/*.json`을 전부 로드해 리스트로 들고 있고, 검색은 부분 문자열 매칭, 거리 계산은 실제 haversine 공식 사용.
  - 즉 **동일한 개념(예: "가까운 장소 찾기")이 두 가지 다른 정확도/구현으로 중복**되어 있고, 프론트엔드는 `/api/*` 경로만 호출한다(아래 5절). `/festivals`, `/chat` 등 JSON 기반 엔드포인트는 현재 프론트에서 전혀 호출되지 않는 "죽은 코드에 가까운" 상태로 보인다(수동 테스트/Swagger용으로 추정).
- `database.py`와 `orm.py`가 **중복**으로 존재 — 둘 다 SQLite 연결/세션을 만드는데, `database.py`(raw `sqlite3.connect`, row_factory만 설정)는 실제로 `main.py`/`services.py` 어디에서도 import되지 않는다. 실사용은 `orm.py`(SQLAlchemy `SessionLocal`)뿐.
- 최근 git 미커밋 diff: `backend/app/main.py`에서 `from data_loader import ...` → `from app.data_loader import ...`로 상대import를 패키지import로 고친 흔적(패키지화 리팩터링 진행 중임을 시사).

### 4-3. 챗봇 로직 상세 (`build_prompt` + `/chat`)
1. 사용자의 `question`으로 `search_festival`(제목/주소 부분일치, 상위 5개) 실행
2. `lat`/`lon`이 오면 `nearby_items`(반경 5km, 상위 5개) 추가
3. 두 결과를 `contentid` 기준 dict로 중복 제거 후 최대 10개를 "소스"로 채택
4. 소스가 하나도 없으면 **404 에러 반환**(챗봇이 아예 답하지 않음 — 데이터에 없는 일반 대화도 전부 거부)
5. 소스 텍스트 + "데이터 밖 정보 추정 금지" 지시를 포함한 프롬프트를 만들어 `openai.ChatCompletion.create(model="gpt-3.5-turbo", ...)` 호출

**중요 결함**: `backend/requirements.txt`는 `openai>=1.0.0`을 명시하지만, `openai_client.py`는 **openai 0.x 레거시 API**(`openai.api_key = ...`, `openai.ChatCompletion.create(...)`)를 그대로 쓰고 있다. openai SDK 1.0+ 에서는 이 인터페이스가 제거되어 `AttributeError`가 발생한다 — **현재 코드로는 `/chat`이 실제로는 동작하지 않을 가능성이 매우 높다.** (`OpenAI(api_key=...).chat.completions.create(...)` 형태로 마이그레이션 필요.)

---

## 5. 프론트엔드 (Vue 3 + Vite)

- 라우팅: `/`(`FestivalListPage`) , `/festivals/:festivalId`(`FestivalDetailPage`) 단 2개 뿐
- `FestivalListPage`: `GET /api/festivals?keyword=` 호출 → `FestivalCard` 그리드 렌더(썸네일/제목/주소)
- `FestivalDetailPage`: `GET /api/festivals/{id}` + `GET /api/festivals/{id}/nearby` 병렬 호출 → 상세정보 + 주변 장소 리스트/지도 표시
- **지도 컴포넌트는 완전 플레이스홀더**: `FestivalMap.vue`, `MapPreview.vue` 둘 다 실제 지도 라이브러리(Leaflet/Kakao Maps) 연동 없이 정적 텍스트/CSS 박스만 그림("지도 영역입니다" 문구, `.map-pin`/`.map-marker` 로 위치만 흉내)
- **챗봇 UI 미구현**: `App.vue`에 플로팅 버튼(`💬`)은 있지만 `@click` 핸들러/채팅창 컴포넌트가 전혀 없다 — 순수 장식 요소. `/chat` API를 호출하는 프론트 코드는 저장소 전체에 존재하지 않음.
- **커뮤니티 게시판 UI/CRUD 화면 전무**: 페이지/컴포넌트 어디에도 게시글 작성/조회/수정/삭제, 비밀번호 입력 폼이 없음.
- `vite.config.js`가 `/api` 요청을 `http://127.0.0.1:8001`로 프록시 — 즉 프론트는 `backend/app`(포트 8001)을 겨냥하고 `project/`(포트 8000)는 겨냥하지 않음. `project/`는 사실상 레거시.
- `run_frontend.py`: `npm run dev -- --host 0.0.0.0 --port 5173`을 서브프로세스로 띄우는 헬퍼 스크립트.

---

## 6. RFP 대비 현재 구현 상태 (핵심 갭 분석)

| RFP 요구사항 | 현재 상태 |
|---|---|
| 익명 게시판 CRUD(비밀번호 검증) | **미구현.** `Place` 모델/엔드포인트만 존재, 게시글(post) 테이블·API·화면 전무 |
| 커뮤니티 데이터 DB 저장 | 해당 없음(게시판 자체가 없음) |
| `POST /api/chat` 챗봇 | 유사 기능(`POST /chat`, `/api` 프리픽스 없음)은 존재하나 openai SDK 버전 불일치로 **동작 불가 가능성 높음**, 프론트 연동 전무 |
| 채팅 UI(히스토리 유지, 모바일, 플로팅) | 플로팅 버튼만 있고 실제 채팅창/히스토리 없음 |
| Vue.js 3 SPA | ✅ 충족 (Vite + vue-router) |
| FastAPI + SQLite + SQLAlchemy | ✅ 충족(단, ORM/raw sqlite3 중복 파일 정리 필요) |
| 제공 JSON 기반 개발 | ✅ 충족(서울만) |
| 배포(Netlify/Render) | 설정 파일(예: `netlify.toml`, `render.yaml`, 빌드 스크립트) 미발견 — 아직 미구성 |
| `.env` 기반 민감정보 관리 | 저장소에 `.env` 파일 없음(정상, `.gitignore`에도 포함됨) — 다만 로컬에 `OPENAI_API_KEY`를 설정해야 `/chat`이 동작하는데 이를 위한 `.env.example` 등 안내 파일도 없음 |
| 외부 AI 코딩 도구 사용 금지 | ⚠️ **정책 충돌 여지** — 본 리서치 자체가 Claude Code로 수행됨 (1절 경고 참조) |
| 데이터 출처/라이선스 문서화 | ✅ 이미 매우 잘 되어 있음(`data/*/SOURCE.md`, `SCHEMA.md`) |
| 선택 기능(지도/시각화/캘린더 등) | 지도는 틀만 있고 미구현, 나머지 선택 기능(차트, 캘린더, 날씨, 다국어 등) 전무 |

---

## 7. 기술적 이슈 / 정리가 필요한 부분

1. **openai SDK 버전 불일치** (4-3절) — `/chat` 즉시 실패 가능성. 최우선 수정 대상.
2. **백엔드 이원화** — `project/`(레거시, 8000번 포트)와 `backend/app/`(정식, 8001번 포트)가 같은 DB 파일(`project/seoul_festival.db`)을 공유하며 공존. 제출 산출물 혼선 방지를 위해 `project/`를 정리하거나 명확히 "사용 안 함"으로 표시할 필요.
3. **`backend/app/database.py` vs `orm.py` 중복** — 전자는 미사용 데드코드.
4. **거리 계산 불일치** — `services.py`(ORM 경로)는 위경도 제곱합으로 근사, `data_loader.py`(JSON 경로)는 정확한 haversine(km). 두 코드가 같은 개념을 다르게 구현.
5. **데이터 경로 하드코딩** — 서울 외 4개 권역 데이터를 프로젝트가 로드하지 않음. 왜 함께 제공됐는지, 다른 팀원이 다른 권역을 담당하는지 확인 필요해 보임.
6. **DB 경로 계산**: `orm.py`/`database.py`가 `Path(__file__).resolve().parents[1] / ".." / "project" / "seoul_festival.db"` 형태로 `parents[1]`(즉 `backend/`)에서 다시 `..`으로 한 단계 더 올라가 `ai_project/project/seoul_festival.db`를 가리킴 — 경로는 맞지만 `parents[1] / ".."`처럼 불필요하게 에둘러 계산되어 있어 가독성이 떨어짐.
7. **CORS**: `allow_origins=["*"]` + `allow_credentials=True` 조합은 실무 관례상 지양되나, 인증이 없는 이 프로젝트 특성상 실질적 위험은 낮음.

---

## 8. 실행 방법 요약 (문서 기준)

**백엔드(정식, backend/app)**
```powershell
cd backend
pip install -r requirements.txt
python run_server.py   # 0.0.0.0? 아님, 127.0.0.1:8001 (PORT 환경변수로 변경 가능)
```
DB가 비어있다면 먼저 `python app/import_seoul_data.py` 실행 필요(스키마 재생성 후 서울 JSON 적재).

**프론트엔드**
```powershell
cd frontend
npm install
npm run dev   # http://localhost:5173, /api는 8001로 프록시
```

**레거시 프로토타입(project/, 참고용)**
```powershell
cd project
.\.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

---

## 9. 결론 요약

이 저장소는 SSAFY 팀 과제 "LocalHub"의 진행 중인 구현체다. 기술 스택(Vue3+FastAPI+SQLite)과 데이터 파이프라인(TourAPI JSON → SQLite, 출처/라이선스 문서화)은 견고하게 갖춰졌고, 축제 목록/상세 조회 CRUD의 읽기 경로는 동작 가능한 수준이다. 반면 RFP의 두 핵심 축인 **① 익명 게시판(비밀번호 기반 CRUD)** 과 **② 실제로 동작하는 챗봇+채팅 UI**는 아직 실질적으로 비어 있거나(게시판) SDK 버전 문제로 깨져 있을 가능성이 높다(챗봇). 납기(2026-07-16 15:00)가 임박한 점을 고려하면 우선순위는 (1) openai 클라이언트 마이그레이션, (2) 게시판 테이블/CRUD API/화면 신규 구현, (3) 챗봇 프론트 연동, (4) 배포 설정 순으로 보인다.
