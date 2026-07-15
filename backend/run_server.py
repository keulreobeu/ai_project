import os
import uvicorn
from app.orm import ENGINE, Base
from app.models import Place, CommunityPost  # 모든 모델 임포트

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
