# Seoul Festival Explorer

This project implements a small Seoul festival explorer using:
- FastAPI for the backend API
- Vue 3 for the frontend UI
- SQLite with SQLAlchemy for festival data

## Run locally

### Backend

```bash
cd backend
python run_server.py
```

The API will be available at http://127.0.0.1:8001.

### Frontend

```bash
cd frontend
npm install
python run_frontend.py
```

The UI will be available at http://127.0.0.1:5173.

## Verify API

```bash
curl http://127.0.0.1:8001/api/health
curl http://127.0.0.1:8001/api/festivals
```

## Chatbot API

`POST /api/chat` is a DB-backed RAG chatbot over the `places` table. It requires `OPENAI_API_KEY`
to be set in the environment (or a `.env` file, never committed) before it can answer.

```bash
# Step 1: free-text question -> festival candidates
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"이번 주말 축제 추천해줘"}'

# Step 2: pick one festival from the previous response's sources[].id, then ask for a
# nearby category ("관광지" | "문화시설" | "레포츠" | "숙박" | "쇼핑") sorted by distance
curl -X POST http://127.0.0.1:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"주변 숙박 추천해줘","festival_id":1,"category":"숙박"}'
```

## Single-port production build

For deployment, FastAPI serves the built Vue app directly, so only one port needs to be exposed.

```bash
cd frontend
npm install
npm run build        # produces frontend/dist

cd ../backend
pip install -r requirements.txt
python run_server.py # serves API + frontend/dist together on $PORT (default 8001)
```

Open `http://127.0.0.1:8001/` — it serves the built SPA, and any client-side route
(e.g. `http://127.0.0.1:8001/festivals/1`) works on a hard refresh because `app/main.py`
falls back to `index.html` for unmatched non-API paths.

For local development with hot reload, keep using the two-process setup above (`npm run dev`
on 5173 + `python run_server.py` on 8001, wired together by Vite's `/api` proxy) instead of the
single-port build.
