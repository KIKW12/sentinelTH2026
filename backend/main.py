from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Sentinel API", version="1.0.0")

# CORS middleware
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to Sentinel API",
        "version": "1.0.0",
        "description": "Multi-Agent Security Scanner"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "sentinel-api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
