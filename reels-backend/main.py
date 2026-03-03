from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import connect_db
from routers import videos
from routers import reels
import os
import uvicorn

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

# Create storage directories
os.makedirs("storage/uploads", exist_ok=True)
os.makedirs("storage/reels", exist_ok=True)
os.makedirs("storage/thumbnails", exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app.get("/")
def root():
    return {"message": "Reels API is running"}

app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(reels.router, prefix="/api/reels", tags=["Reels"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)