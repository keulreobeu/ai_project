from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services import fetch_festival_detail, fetch_festivals, fetch_nearby_places


from pathlib import Path
from typing import List, Optional

from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.data_loader import PlaceItem, SeoulDataStore
from app.openai_client import OpenAIClient


DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "서울"
TEST_PAGE_PATH = Path(__file__).resolve().parent / "test_page.html"


app = FastAPI(title="Seoul Festival API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 데이터 로드 및 OpenAI 클라이언트 초기화
data_store = SeoulDataStore(DATA_ROOT)
openai_client = OpenAIClient()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/festivals")
def list_festivals(keyword: str | None = None):
    return fetch_festivals(keyword=keyword)


@app.get("/api/festivals/{festival_id}")
def get_festival(festival_id: int):
    festival = fetch_festival_detail(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="festival not found")
    return festival


@app.get("/api/festivals/{festival_id}/nearby")
def get_nearby_places(festival_id: int):
    return fetch_nearby_places(festival_id)



class ChatRequest(BaseModel):
    question: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    location_name: Optional[str] = None
    persona: Optional[str] = None
    event_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[PlaceItem]


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "source_count": len(data_store.all_items),
        "loaded_categories": list(data_store.categories.keys()),
    }


@app.get("/test-page")
def test_page() -> FileResponse:
    return FileResponse(TEST_PAGE_PATH)


@app.get("/festivals", response_model=List[PlaceItem])
def festival_search(q: str = Query(..., description="검색어(축제/공연명 또는 지역)"), limit: int = 10):
    return data_store.search_festival(q, limit=limit)


@app.get("/nearby", response_model=List[PlaceItem])
def nearby_search(
    lat: float = Query(..., description="위도"),
    lon: float = Query(..., description="경도"),
    radius_km: float = Query(3.0, description="반경(km)"),
    categories: Optional[List[str]] = Query(None, description="검색할 카테고리 목록"),
    limit: int = Query(20, description="최대 반환 개수"),
):
    allowed_categories = None
    if categories:
        allowed_categories = [category.strip().lower() for category in categories]
    return data_store.nearby_items(lat, lon, categories=allowed_categories, radius_km=radius_km, limit=limit)


@app.get("/itinerary")
def itinerary(event_id: str = Query(..., description="축제/공연 contentid"), radius_km: float = Query(3.0)):
    try:
        return data_store.nearby_itinerary(event_id, radius_km=radius_km)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/persona-recommend", response_model=List[PlaceItem])
def persona_recommend(
    persona: Optional[str] = Query(None, description="추천 대상 페르소나, 예: 아이와 함께, 연인, 혼자"),
    lat: Optional[float] = Query(None, description="위도"),
    lon: Optional[float] = Query(None, description="경도"),
    radius_km: float = Query(5.0, description="반경(km)"),
    limit: int = Query(10, description="최대 반환 개수"),
):
    return data_store.recommend_for_persona(persona=persona, lat=lat, lon=lon, radius_km=radius_km, limit=limit)


def build_prompt(question: str, sources: List[PlaceItem]) -> str:
    source_text = "\n".join(
        f"- {item.title} ({item.contentType})\n  주소: {item.display_address()}\n  전화: {item.tel or '정보 없음'}\n  카테고리: {item.category}\n  거리: {item.distance_km:.1f}km"
        for item in sources
    )
    if not source_text:
        source_text = "현재 주어진 데이터 소스가 없습니다."

    return (
        "당신은 서울 지역 여행을 돕는 챗봇입니다. 아래 제공된 데이터 소스를 활용하여 유저의 질문에 답하세요. "
        "주어진 데이터를 벗어난 정보는 추정하지 말고, 알 수 없으면 '해당 데이터에서 찾을 수 없습니다'라고 솔직하게 답하세요.\n\n"
        f"사용자 질문: {question}\n\n"
        "---\n"
        "데이터 소스 목록:\n"
        f"{source_text}\n"
        "---\n"
        "답변은 한국어로 작성하고, 필요한 경우 추천 항목 이름과 주소를 함께 제시하세요."
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    festival_sources = data_store.search_festival(request.question, limit=5)
    nearby_sources: List[PlaceItem] = []
    if request.lat is not None and request.lon is not None:
        nearby_sources = data_store.nearby_items(request.lat, request.lon, radius_km=5.0, limit=5)

    source_candidates = festival_sources + nearby_sources
    unique_sources = {item.contentid: item for item in source_candidates}.values()
    sources = list(unique_sources)[:10]

    if not sources:
        raise HTTPException(status_code=404, detail="질문에 맞는 서울 데이터 소스를 찾을 수 없습니다.")

    prompt = build_prompt(request.question, sources)
    try:
        answer = openai_client.chat_completion(
            messages=[
                {"role": "system", "content": "서울 지역 축제/공연 추천 챗봇입니다. 아래 가이드에 따라 답변하세요."},
                {"role": "user", "content": prompt},
            ],
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(answer=answer, sources=sources)
