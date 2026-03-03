# reels-backend/models/reel.py

from beanie import Document
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Subtitle segment — same shape as Whisper output
class SubtitleSegment(BaseModel):
    start: float
    end: float
    text: str

class Reel(Document):
    video_id: str                              # ref to Video (like mongoose ref)
    
    # Clip settings
    start_time: float = 0
    end_time: float = 60
    
    # AI Processing results
    focal_x: Optional[int] = None             # detected subject X position
    focal_y: Optional[int] = None             # detected subject Y position
    transcript: Optional[str] = None          # full whisper transcript
    subtitle_segments: List[SubtitleSegment] = []
    subtitle_path: Optional[str] = None       # .srt file path
    
    # Headline
    headline: Optional[str] = None            # active headline (editable)
    headline_options: List[str] = []          # all AI suggestions
    
    # Output
    reel_path: Optional[str] = None           # final video path
    thumbnail_path: Optional[str] = None
    
    # Status tracking
    status: str = "pending"                   
    # pending | detecting | cropping | 
    # subtitles | headline | finalizing | ready | failed
    processing_percent: int = 0
    error_message: Optional[str] = None
    
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None

    class Settings:
        name = "reels"                        # MongoDB collection name