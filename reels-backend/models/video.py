# reels-backend/models/video.py

from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Video(Document):
    filename: str                        # original file name
    original_path: str                   # where file is stored
    thumbnail_path: Optional[str] = None
    duration: Optional[float] = None     # in seconds
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    size_mb: Optional[float] = None
    status: str = "uploaded"             # uploaded | processing | done
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "videos"                  # MongoDB collection name

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "interview.mp4",
                "duration": 120.5,
                "status": "uploaded"
            }
        }