from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import import_bookmarks

app = FastAPI(
    title="BookmarkAI",
    description="AI-powered bookmark manager",
    version="0.1.0",
)

# Set up CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def read_root():
    return {"status": "ok"}

app.include_router(import_bookmarks.router, prefix="/api/v1/import", tags=["v1"])
