# Sentinel API Backend

FastAPI backend for the Sentinel security scanner.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Or using Python directly
python main.py
```

## API Docs

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
