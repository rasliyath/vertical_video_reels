# reels-backend/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.video import Video
from models.reel import Reel
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "reels_db")

async def connect_db():
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(
        database=client[DB_NAME],
        document_models=[Video, Reel]   # like registering mongoose models
    )
    print("✅ MongoDB Connected")