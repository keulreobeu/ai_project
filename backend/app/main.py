from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services import (
    fetch_festival_detail, fetch_festivals, fetch_nearby_places,
    create_community_post, get_community_posts, get_community_post,
    update_community_post, delete_community_post
)
from app.schemas import CommunityPostCreate, CommunityPostUpdate
from pydantic import BaseModel
from app.orm import SessionLocal
from app.models import CommunityPost
from app.services import _verify_password

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


# Community Posts APIs
@app.post("/api/community/posts")
def create_post(post_data: CommunityPostCreate):
    try:
        return create_community_post(post_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community/posts")
def list_posts(category: str = "general"):
    try:
        return get_community_posts(category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community/posts/{post_id}")
def get_post(post_id: int):
    try:
        post = get_community_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="post not found")
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PasswordVerifyRequest(BaseModel):
    password: str

@app.post("/api/community/posts/{post_id}/verify-password")
def verify_post_password(post_id: int, payload: PasswordVerifyRequest):
    db = SessionLocal()
    try:
        post = db.query(CommunityPost).filter(CommunityPost.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="post not found")

        return {"valid": _verify_password(payload.password, post.password)}
    finally:
        db.close()

@app.put("/api/community/posts/{post_id}")
def update_post(post_id: int, post_data: CommunityPostUpdate):
    if not post_data.password:
        raise HTTPException(status_code=422, detail="password is required")

    try:
        updated_post = update_community_post(post_id, post_data, post_data.password)
        if not updated_post:
            raise HTTPException(status_code=401, detail="invalid password or post not found")
        return updated_post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/community/posts/{post_id}")
def delete_post(post_id: int, password: str = Query(...)):
    try:
        success = delete_community_post(post_id, password)
        if not success:
            raise HTTPException(status_code=401, detail="invalid password or post not found")
        return {"message": "post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))