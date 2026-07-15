# Seoul Local Festival Chatbot API 구조 및 동작 정리

이 문서는 `project` 폴더 아래에 생성된 FastAPI 기반 챗봇 백엔드의 주요 모듈과 동작 방식을 정리합니다.

## 구성 파일

- `data_loader.py`: 서울 지역 JSON 데이터를 로드하고, 검색/거리 계산/추천 로직을 제공합니다.
- `openai_client.py`: OpenAI API 호출을 추상화합니다.
- `main.py`: FastAPI 서버 정의 및 챗봇 API 엔드포인트를 구현합니다.

---

## `data_loader.py`

### 핵심 역할

- `SeoulDataStore` 클래스 생성
- JSON 데이터를 로드하여 `PlaceItem` 모델로 파싱
- 거리 기반 탐색 및 추천 기능 제공

### 주요 클래스와 함수

#### `PlaceItem`
- `pydantic.BaseModel`을 상속하는 데이터 모델
- 필드: `contentid`, `title`, `addr1`, `addr2`, `mapx`, `mapy`, `contentType`, `category` 등
- `with_distance(lat, lon)`: 주어진 좌표와의 거리를 계산해 `distance_km`를 추가한 복사본을 반환
- `display_address()`: `addr1`과 `addr2`를 결합한 주소 문자열 반환

#### `haversine(lat1, lon1, lat2, lon2)`
- 두 지점 간 거리를 킬로미터 단위로 계산
- 위도/경도를 라디안으로 변환하고 하버사인 공식을 사용

#### `load_json(path)`
- UTF-8-sig 인코딩으로 JSON 파일을 로드

#### `parse_item(raw, category_key)`
- 원시 JSON 객체를 `PlaceItem`으로 변환
- `mapx`, `mapy`를 `float`로 파싱
- `contentType`을 카테고리별 기본 제목으로 보정

### `SeoulDataStore`

#### 초기화
- `data_root` 위치에서 `CATEGORY_FILES`에 정의된 모든 서울 데이터를 로드
- `self.categories`에 카테고리별 목록 저장
- `self.all_items`에 전체 항목 통합 저장

#### 검색 및 추천 메서드

- `search_festival(query, limit=10)`: 축제/공연 제목과 주소를 기반으로 부분 문자열 검색
- `find_by_id(contentid, category=None)`: `contentid`로 항목 조회
- `nearby_items(lat, lon, categories=None, radius_km=3.0, limit=20)`: 지정 반경 내 위치 기반 탐색
- `nearby_itinerary(event_id, radius_km=3.0)`: 특정 축제/공연 주변의 `lodging`, `shopping`, `culture`, `tourist` 추천
- `recommend_for_persona(persona, lat, lon, radius_km=5.0, limit=10)`: 페르소나(아이/가족/연인/혼자)에 따라 추천 카테고리 지정, 위치가 있으면 거리 기반 반환
- `format_items_as_text(items)`: 항목 목록을 텍스트 형태로 정리

---

## `openai_client.py`

### 핵심 역할

- OpenAI API 키를 환경 변수에서 읽음
- OpenAI `ChatCompletion` 요청을 간단한 메서드로 래핑

### 주요 클래스와 메서드

#### `OpenAIClient`
- `self.api_key`: `OPENAI_API_KEY` 환경 변수에서 로드
- `ensure_api_key()`: API 키 미설정 시 예외 발생
- `chat_completion(messages, model='gpt-3.5-turbo', temperature=0.5, max_tokens=500)`: OpenAI ChatCompletion API 호출

---

## `main.py`

### 핵심 역할

- FastAPI 애플리케이션을 생성
- 서울 데이터 저장소와 OpenAI 클라이언트 초기화
- REST API 엔드포인트 정의
- `/chat`에서 질문과 데이터를 결합해 OpenAI로 전달

### 주요 엔드포인트

#### `GET /health`
- 서버 상태 및 로드된 데이터 개수 반환

#### `GET /festivals`
- `q` 검색어로 축제/공연을 검색
- `data_store.search_festival()` 사용

#### `GET /nearby`
- `lat`, `lon`, `radius_km`, `categories`, `limit`을 받아 위치 기반 결과 반환
- `data_store.nearby_items()` 사용

#### `GET /itinerary`
- `event_id` 기반 추천 코스 생성
- `data_store.nearby_itinerary()` 사용

#### `GET /persona-recommend`
- `persona`, 선택적 `lat`, `lon`을 기반으로 추천
- `data_store.recommend_for_persona()` 사용

#### `POST /chat`
- 사용자가 보낸 `question`, `lat`, `lon`, `persona`를 입력 받음
- 축제 검색 결과 + 위치 기반 결과를 소스 후보로 수집
- OpenAI에 전달할 프롬프트를 생성
- 응답 및 활용된 소스 목록을 반환

### OpenAI 프롬프트 생성

`build_prompt(question, sources)`에서:
- 챗봇 역할을 "서울 지역 여행을 돕는 챗봇"으로 정의
- 검색된 소스 리스트를 텍스트 형태로 포함
- "데이터를 벗어난 정보는 추정하지 말 것"을 명시
- 한국어 답변 요청

---

## 동작 흐름 요약

1. 서버 시작 시 `SeoulDataStore`가 `data/서울` 폴더의 JSON 파일을 모두 로드
2. API 요청이 들어오면 해당 엔드포인트가 `data_store` 메서드를 호출
3. `/chat` 요청 시 검색된 데이터 소스와 질문을 합쳐 OpenAI에 전달
4. OpenAI 응답과 함께 데이터 소스 항목을 클라이언트에 반환

---

## 실행 방법

```bash
cd project
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`OPENAI_API_KEY`가 설정되어 있어야 `/chat`가 정상 동작합니다.



# Seoul Local Festival Chatbot API

서울 지역의 축제, 공연, 관광지, 문화시설, 쇼핑, 숙박 데이터를 활용하는 FastAPI 기반 챗봇 백엔드입니다.

## 주요 기능

- 축제/공연 검색: `/festivals?q=서울빛초롱축제`
- 위치 기반 추천: `/nearby?lat=37.5&lon=127.0&radius_km=3`
- 축제 기반 코스 추천: `/itinerary?event_id=2556687`
- 페르소나 추천: `/persona-recommend?persona=아이와 함께&lat=37.5&lon=127.0`
- OpenAI 챗봇 답변: `/chat`

## 설치

```powershell
cd project
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 환경 변수

OpenAI API 키를 설정합니다.

```powershell
setx OPENAI_API_KEY "your-openai-key"
```

또는 프로젝트에서 `.env` 파일을 사용합니다.

## 실행

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 예시 요청

- `GET /festivals?q=축제`
- `GET /nearby?lat=37.573&lon=126.976&radius_km=2`
- `GET /itinerary?event_id=2556687`
- `POST /chat`

### `/chat` 요청 예시

```json
{
  "question": "강남역 근처에서 지금 하는 행사나 공연 추천해줘",
  "lat": 37.4979,
  "lon": 127.0276,
  "persona": "연인"
}
```

## 데이터 위치

이 서비스는 `../data/서울` 폴더의 JSON 파일을 사용합니다. 프로젝트 폴더에서 실행할 때 해당 경로가 유효해야 합니다.
