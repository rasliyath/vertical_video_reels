# reels-backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from database import connect_db
from routers import videos, reels
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield

app = FastAPI(title="Reels API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage folders
os.makedirs("storage/uploads", exist_ok=True)
os.makedirs("storage/reels", exist_ok=True)
os.makedirs("storage/thumbnails", exist_ok=True)
os.makedirs("storage/subtitles", exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# API routes first
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(reels.router, prefix="/api/reels", tags=["Reels"])

# Serve React static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=f"{STATIC_DIR}/assets"), name="react-assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(f"{STATIC_DIR}/index.html")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        # Don't intercept API or storage routes
        if full_path.startswith("api/") or full_path.startswith("storage/"):
            return {"error": "Not found"}
        return FileResponse(f"{STATIC_DIR}/index.html")
else:
    @app.get("/")
    def root():
        return {"message": "Reels API is running"}