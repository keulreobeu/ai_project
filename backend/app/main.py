import mimetypes

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services import fetch_festival_detail, fetch_festivals, fetch_nearby_places


from pathlib import Path
from typing import List, Optional, Tuple

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 일부 Windows 환경은 mimetypes 레지스트리에 .js가 text/plain으로 잘못 등록되어 있어
# StaticFiles가 Vue 빌드 산출물(ES 모듈 스크립트)을 잘못된 MIME 타입으로 서빙하는 문제가 있다.
# 브라우저는 <script type="module">에 대해 MIME 타입을 엄격히 검사하므로 명시적으로 바로잡는다.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

from app import services
from app.data_loader import PlaceItem, SeoulDataStore
from app.models import Place
from app.openai_client import OpenAIClient


DATA_ROOT = Path(__file__).resolve().parent.parent.parent / "data" / "서울"
TEST_PAGE_PATH = Path(__file__).resolve().parent / "test_page.html"
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


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


# ---------------------------------------------------------------------------
# /api/chat: DB(`places` 테이블) 기반 RAG 챗봇 — 1단계(축제 검색) / 3단계(축제 앵커 거리순 추천)
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ApiChatRequest(BaseModel):
    question: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    festival_id: Optional[int] = None  # 2단계에서 사용자가 고른 축제(앵커)
    category: Optional[str] = None     # 3단계에서 고른 카테고리: "관광지" | "문화시설" | "레포츠" | "숙박" | "쇼핑"
    history: List[ChatMessage] = []


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


def build_festival_prompt(
    question: str,
    festivals: List[Place],
    companion_hint: Optional[str] = None,
) -> str:
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
    distance_by_id: dict[int, float] = {}

    if request.festival_id is not None and request.category:
        # 3단계: 축제 앵커 + 카테고리 → 거리순 추천
        anchor = services.get_place(request.festival_id)
        if not anchor:
            raise HTTPException(status_code=404, detail="선택한 축제를 찾을 수 없습니다.")
        scored = services.nearby_by_category_from_anchor(anchor, request.category)
        places: List[Place] = [p for p, _ in scored]
        distance_by_id = {p.place_id: d for p, d in scored}
        prompt = build_nearby_prompt(anchor, request.category, scored)
    else:
        # 1단계: 자유 텍스트 → 축제 후보 검색 (지역은 키워드 검색이, 동행 힌트는 재정렬이 이미 반영)
        places = services.search_festivals_for_chat(request.question, lat=request.lat, lon=request.lon)
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
            id=p.place_id,
            title=p.title or "",
            address=p.address1,
            tel=p.tel,
            category=p.content_type_id,
            distance_km=distance_by_id.get(p.place_id),
        )
        for p in places
    ]
    return ApiChatResponse(answer=answer, sources=sources)


# ---------------------------------------------------------------------------
# 단일 포트 배포: Vue 빌드 산출물(frontend/dist) 정적 서빙 + SPA 폴백
# 반드시 파일 맨 끝(다른 모든 /api/... 라우트 등록 이후)에 위치해야 한다 —
# FastAPI는 등록 순서대로 라우트를 매칭하므로, catch-all이 먼저 있으면 API 요청까지 가로챈다.
# ---------------------------------------------------------------------------

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
