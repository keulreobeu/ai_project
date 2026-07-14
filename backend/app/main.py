from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services import fetch_festival_detail, fetch_festivals, fetch_nearby_places

app = FastAPI(title="Seoul Festival API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
