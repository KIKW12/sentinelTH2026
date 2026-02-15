# Sentinel Backend

This is the Python backend for Sentinel, handling API requests and running the async worker agents.

## Setup

1.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in your Supabase credentials:
    ```bash
    cp .env.example .env
    ```

    - Get `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` from your Supabase Project Settings > API.

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

## Usage

You need to run TWO processes in separate terminals:

### 1. Control Plane (Flask API)
Starts the API server at `http://localhost:5000`.

```bash
python app.py
```

### 2. Execution Plane (Worker)
Starts the worker loop that polls for queued runs and launches agents (Exposure, Headers, etc.).

```bash
python worker.py
```

## triggering a Run (Curl)

Once both are running, you can trigger a scan:

```bash
curl -X POST http://localhost:5000/runs/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "agents": ["exposure", "headers_tls"]
  }'
```
