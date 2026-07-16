# Seoul Festival Explorer

한국관광공사 공공데이터를 기반으로 서울의 축제와 주변 관광 정보를 탐색하고, 익명으로 지역 정보를 공유할 수 있는 커뮤니티 서비스입니다.

- 배포 URL: https://ai-project-vw34.onrender.com/
- API 문서: https://ai-project-vw34.onrender.com/docs
- 기준일: 2026-07-16

## 1. 주요 기능

### 축제·관광 정보

- 서울 축제 목록, 검색, 페이지네이션 및 상세 정보
- 축제 일정 캘린더
- Leaflet 지도와 OpenStreetMap 기반 위치 표시
- 선택한 축제 주변 관광지·문화시설·레포츠·숙박·쇼핑 거리순 추천
- 반응형 Vue SPA와 상세 경로 새로고침 지원

### 익명 커뮤니티

- 회원가입 없이 카테고리별 게시글 목록·상세 조회
- 제목, 내용, 수정용 비밀번호를 이용한 작성·수정·삭제
- 게시글 조회수와 제목 검색
- 커뮤니티 데이터 SQLite 저장

> 비밀번호를 평문으로 저장·비교하는 것은 개발 의뢰서에 명시된 교육 목적의 설계입니다. 실제 운영 서비스에서는 비밀번호 해싱, 인증·인가, 신고 및 개인정보 처리 정책이 필요합니다.

### AI 챗봇

- `POST /api/chat` 기반 플로팅 채팅 UI
- 축제 검색과 주변 장소 추천
- TourAPI 장소 및 커뮤니티 게시글을 근거로 답변과 출처 제공
- 최근 대화 내역 유지와 모바일 화면 대응
- `OPENAI_API_KEY`가 없으면 나머지 기능은 동작하지만 챗봇은 `503`을 반환

## 2. 기술 스택

| 구분 | 기술 |
|---|---|
| Frontend | Vue 3, Vue Router, Vite, Leaflet |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Uvicorn |
| Database | SQLite |
| AI | OpenAI API |
| Deployment | Render Web Service |
| Data | 한국관광공사 TourAPI 4.0, OpenStreetMap |

## 3. 프로젝트 구조

```text
ai_project/
├── backend/              # FastAPI 애플리케이션과 API
│   ├── app/
│   ├── .env.example
│   ├── requirements.txt
│   └── run_server.py
├── frontend/             # Vue 3 SPA
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── data/                 # 5개 권역 TourAPI 원본 JSON
├── project/
│   ├── seoul_festival.db # 초기 데이터가 포함된 SQLite DB
│   └── *.py              # 데이터 병합·보강 스크립트
├── render.yaml           # Render 배포 설정
├── requirements.txt      # Render용 Python 의존성 진입점
└── README.md
```

## 4. 로컬 실행

### 사전 요구사항

- Python 3.11
- Node.js 22 권장
- npm

### 설치

저장소 루트에서 다음을 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cd frontend
npm ci
cd ..

Copy-Item backend/.env.example backend/.env
```

`backend/.env`에 필요한 값을 입력합니다. 실제 `.env`와 API 키는 Git에 올리지 않습니다.

### 개발 서버

터미널 1:

```powershell
cd backend
python run_server.py
```

터미널 2:

```powershell
cd frontend
npm run dev
```

- 웹: http://127.0.0.1:5173
- API: http://127.0.0.1:8001
- Swagger: http://127.0.0.1:8001/docs

Vite 개발 서버는 `/api` 요청을 FastAPI로 프록시하므로 화면을 보면서 코드를 수정하면 즉시 반영됩니다.

### 배포 방식과 동일하게 실행

```powershell
cd frontend
npm ci
npm run build

cd ../backend
python run_server.py
```

이 경우 FastAPI가 `frontend/dist`의 Vue 앱과 API를 단일 포트 `8001`에서 함께 제공합니다.

## 5. 환경변수

| 변수 | 필수 | 기본값/용도 |
|---|---|---|
| `DB_PATH` | 아니요 | `project/seoul_festival.db` |
| `DATABASE_URL` | 아니요 | 지정 시 `DB_PATH`보다 우선 |
| `CORS_ORIGINS` | 아니요 | 허용 프런트 주소를 쉼표로 구분 |
| `OPENAI_API_KEY` | 챗봇 사용 시 | OpenAI API 키 |
| `OPENAI_MODEL` | 아니요 | `gpt-4o-mini` |
| `PORT` | 아니요 | 로컬 `8001`, Render가 자동 지정 |
| `DATA_GO_KR_*` | 데이터 재수집 시 | TourAPI 데이터 가공 스크립트용 |

## 6. 주요 API

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/api/health` | 서버·DB 상태 확인 |
| GET | `/api/festivals` | 축제 목록·검색·페이지네이션 |
| GET | `/api/festivals/calendar` | 월별 축제 일정 |
| GET | `/api/festivals/{id}` | 축제 상세 |
| GET | `/api/festivals/{id}/nearby` | 주변 장소 추천 |
| GET | `/api/community/posts` | 카테고리별 게시글 목록 |
| POST | `/api/community/posts` | 게시글 작성 |
| GET | `/api/community/posts/{id}` | 게시글 상세 |
| POST | `/api/community/posts/{id}/verify-password` | 수정 비밀번호 확인 |
| PUT | `/api/community/posts/{id}` | 게시글 수정 |
| DELETE | `/api/community/posts/{id}` | 게시글 삭제 |
| POST | `/api/chat` | 지역 정보 챗봇 |

전체 요청·응답 형식은 실행 중인 `/docs`에서 확인할 수 있습니다.

## 7. 데이터베이스

`project/seoul_festival.db`는 별도 DB 서버 없이 동작하는 SQLite 파일이며 초기 서울 관광 데이터 6,518건을 포함합니다.

주요 테이블:

- `regions`: 권역 정보
- `content_types`: 관광 콘텐츠 유형
- `places`: 축제·관광지·문화시설·숙박 등 장소 정보
- `festival_details`: 축제 기간과 상세 정보
- `festival_related_places`: 축제 주변 장소 관계
- `community_posts`: 현재 UI에서 사용하는 익명 게시글
- `posts`: 초기 커뮤니티 스키마

Render 무료 인스턴스의 로컬 파일시스템은 재배포·재시작 시 초기화될 수 있습니다. 게시글을 영구 보존하려면 Persistent Disk를 연결하고 `DB_PATH`를 해당 경로로 지정해야 합니다.

## 8. Render 배포

이 저장소는 PDF 제안서의 Netlify·Render 분리 배포 대신, CORS와 운영 복잡도를 줄이기 위해 Render 단일 서비스로 구성했습니다.

`render.yaml`의 동작:

1. Python 패키지 설치
2. `frontend`에서 `npm ci && npm run build`
3. `backend/run_server.py` 실행
4. FastAPI가 API와 빌드된 Vue SPA를 함께 제공
5. `/api/health`로 상태 확인

Render Dashboard에서 다음 환경변수를 Secret으로 등록합니다.

```text
OPENAI_API_KEY=실제_API_키
OPENAI_MODEL=gpt-4o-mini
```

API 키와 `.env` 파일은 저장소에 커밋하지 않습니다.

## 9. 데이터 출처 및 라이선스

### 한국관광공사 TourAPI 4.0

- 제공기관: 한국관광공사
- 공식 데이터명: 한국관광공사_국문 관광정보 서비스_GW
- 공식 페이지: https://www.data.go.kr/data/15101578/openapi.do
- 이용허락범위: 제한 없음
- 저장 위치: `data/**/*.json`, `project/seoul_festival.db`
- 수집·확인 기준일: 2026-07-16

저장소 데이터 현황:

| 권역 | JSON 파일 | 레코드 | 포함 유형 |
|---|---:|---:|---|
| 서울 | 7 | 6,518 | 음식점 제외 7종 |
| 대전·충청 | 8 | 1,365 | 8종 |
| 구미·경북 | 8 | 1,667 | 8종 |
| 광주·전라 | 8 | 1,393 | 8종 |
| 부산 | 7 | 1,759 | 음식점 제외 7종 |
| 합계 | 38 | 12,702 |  |

TourAPI 사진에는 공공누리 제1유형과 제3유형이 혼재합니다. 이미지별 유형을 확인하지 못한 경우 출처를 표시하고 자르기·합성·색상 변경 등의 변형을 피해야 합니다. 사진에 포함된 인물·상표 등에 대한 제3자 권리는 별도 확인이 필요합니다.

권장 출처 표기:

```text
관광정보 및 이미지는 한국관광공사 TourAPI 4.0을 활용했습니다.
출처: 한국관광공사
```

### OpenStreetMap

- 지도 데이터: © OpenStreetMap contributors
- 라이선스: Open Data Commons Open Database License 1.0 (ODbL)
- 저작권: https://www.openstreetmap.org/copyright
- 타일 정책: https://operations.osmfoundation.org/policies/tiles/

지도 위의 출처 표시는 제거하면 안 됩니다. 표준 타일 서버의 대량 다운로드·오프라인 사전 수집을 금지하며, 트래픽이 커지면 별도 타일 제공자를 사용해야 합니다.

### 사용자 작성글과 AI 답변

- 커뮤니티 글은 사용자가 직접 입력한 데이터로 TourAPI 라이선스 대상이 아닙니다.
- 게시글 이용·삭제·신고 정책과 개인정보 처리방침은 실제 운영 전에 마련해야 합니다.
- AI 답변은 공식 관광정보가 아닌 참고용이며 행사 정보는 공식 채널에서 다시 확인해야 합니다.
- 게시글 비밀번호와 개인정보를 데이터 출처나 챗봇 응답에 노출하지 않습니다.

## 10. 요구사항 구현 현황

| 개발 의뢰서 항목 | 구현 상태 | 구현 내용 |
|---|---|---|
| 제공 JSON 연동 | 완료 | 서울 데이터 6,518건 SQLite 적재 |
| 익명 커뮤니티 CRUD | 완료 | 비밀번호 기반 작성·조회·수정·삭제 |
| FastAPI REST API | 완료 | 축제, 주변 장소, 게시글, 챗봇 API |
| Vue 3 SPA | 완료 | 반응형 화면과 Vue Router |
| SQLite·SQLAlchemy | 완료 | 초기 DB 파일 포함 |
| 챗봇 | 완료 | OpenAI API 기반 질의응답과 출처 |
| 지도 시각화 | 완료 | Leaflet·OpenStreetMap |
| 축제 캘린더 | 완료 | 월별 일정 표시 |
| 배포 | 완료 | Render 단일 서비스 |
| 민감정보 분리 | 완료 | `.env` 제외, Render Secret 사용 |

## 11. WBS 요약

| 단계 | 주요 작업 | 산출물 | 상태 |
|---|---|---|---|
| 요구사항·데이터 분석 | 개발 의뢰서 분석, 서울 권역 선정, 라이선스 확인 | 요구사항·데이터 명세 | 완료 |
| 데이터베이스 | TourAPI JSON 정제, SQLite 스키마와 초기 데이터 구성 | `project/seoul_festival.db` | 완료 |
| 백엔드 | 축제·주변 장소·커뮤니티·챗봇 API 구현 | `backend/` | 완료 |
| 프런트엔드 | 축제 목록·상세·지도·캘린더·커뮤니티·채팅 UI 구현 | `frontend/` | 완료 |
| 통합·검증 | SPA 연결, CRUD와 주요 API, 프로덕션 빌드 확인 | 통합 애플리케이션 | 완료 |
| 배포 | Render 빌드·실행·헬스체크 구성 | 배포 URL, `render.yaml` | 완료 |
| 문서화 | 실행법, API, 구현 현황, 데이터 출처·라이선스 통합 | `README.md` | 완료 |

## 12. 최종 제출물

| 개발 의뢰서 제출 항목 | 저장·제출 위치 |
|---|---|
| Vue 프런트엔드 소스 | Git 저장소의 `frontend/` |
| FastAPI 백엔드 소스 | Git 저장소의 `backend/` |
| 초기 데이터 포함 SQLite DB | `project/seoul_festival.db` |
| 배포 서비스 URL | https://ai-project-vw34.onrender.com/ |
| 기능 명세·데이터 출처·라이선스 | 이 README의 1, 6, 9, 10절 |
| WBS | 이 README의 11절 |
| 발표 PPT/PDF | 저장소 외부에서 별도 제출 필요 |

> 원 의뢰서에는 Netlify 프런트엔드 URL과 Render 백엔드 URL을 각각 요구하지만, 최종 구현은 Render 단일 URL로 통합했습니다. 제출 시 이 변경 사유와 실제 URL을 함께 안내해야 합니다.

## 13. 운영 전 확인사항

- Render `/api/health`, 메인 화면, SPA 상세 경로 확인
- 게시글 작성·수정·삭제와 재배포 후 데이터 보존 여부 확인
- 챗봇 키·모델·사용량 한도 확인
- TourAPI 및 OpenStreetMap 출처 표시 유지
- HTTPS, 비밀번호 해싱, 인증·인가, 신고 정책 검토
- 이용약관과 개인정보 처리방침 게시

## 라이선스

애플리케이션 소스코드에 대한 별도 오픈소스 라이선스는 지정하지 않았습니다. 외부 데이터와 라이브러리는 각 제공자의 라이선스를 따릅니다.
