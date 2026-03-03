# reels-backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import connect_db
from routers import videos        
from routers import reels          # ← ADD THIS LINE
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield

app = FastAPI(title="Reels API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("storage/uploads", exist_ok=True)
os.makedirs("storage/reels", exist_ok=True)
os.makedirs("storage/thumbnails", exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.get("/")
def root():
    return {"message": "Reels API is running"}

# ↓ MAKE SURE BOTH LINES EXIST
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(reels.router, prefix="/api/reels", tags=["Reels"])  # ← ADD THIS