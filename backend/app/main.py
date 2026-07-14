from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.services import fetch_festival_detail, fetch_festivals, fetch_nearby_places

app = FastAPI(title="Seoul Festival API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/api/festivals")
def list_festivals(keyword: str | None = None, page: int | None = None, limit: int | None = None):
    try:
        return fetch_festivals(page=page, limit=limit, keyword=keyword)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="festival service unavailable") from exc


@app.get("/api/festivals/{festival_id}")
def get_festival(festival_id: int):
    festival = fetch_festival_detail(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="festival not found")
    return festival


@app.get("/api/festivals/{festival_id}/nearby")
def get_nearby_places(festival_id: int):
    try:
        return fetch_nearby_places(festival_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="nearby service unavailable") from exc
