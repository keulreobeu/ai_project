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
