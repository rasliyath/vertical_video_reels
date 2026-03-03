# reels-backend/services/video_service.py

import ffmpeg
import os
import uuid
from datetime import datetime

UPLOAD_DIR = "storage/uploads"
THUMBNAIL_DIR = "storage/thumbnails"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def extract_video_metadata(file_path: str) -> dict:
    """
    Extract duration, resolution, fps from video
    Same as reading file stats in Node.js but for video
    """
    try:
        probe = ffmpeg.probe(file_path)
        
        # Get video stream info
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"),
            None
        )
        
        if not video_stream:
            return {}

        # Calculate FPS from fraction string like "30000/1001"
        fps_raw = video_stream.get("r_frame_rate", "30/1")
        fps_parts = fps_raw.split("/")
        fps = round(int(fps_parts[0]) / int(fps_parts[1]), 2)

        return {
            "duration": float(probe["format"].get("duration", 0)),
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "fps": fps,
            "size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2)
        }

    except Exception as e:
        print(f"Metadata extraction error: {e}")
        return {}


def generate_thumbnail(video_path: str, video_id: str) -> str:
    """
    Extract frame at 2 seconds as thumbnail
    Like sharp() in Node.js but for video frames
    """
    try:
        thumb_filename = f"{video_id}.jpg"
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_filename)

        (
            ffmpeg
            .input(video_path, ss=2)          # seek to 2 seconds
            .output(thumb_path, vframes=1)    # extract 1 frame
            .overwrite_output()
            .run(quiet=True)
        )

        return f"storage/thumbnails/{thumb_filename}"

    except Exception as e:
        print(f"Thumbnail error: {e}")
        return None