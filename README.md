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
