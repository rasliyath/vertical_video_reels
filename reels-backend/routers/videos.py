# reels-backend/routers/videos.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import os
import uuid
from models.video import Video
from services.video_service import extract_video_metadata, generate_thumbnail

router = APIRouter()

UPLOAD_DIR = "storage/uploads"
ALLOWED_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/avi"]
MAX_SIZE_MB = 500


# ─────────────────────────────────────────
# POST /api/videos/upload
# Like: router.post('/upload', upload.single('video'), ...)
# ─────────────────────────────────────────
@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):

    # 1. Validate file type (like multer fileFilter)
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only MP4, MOV, AVI allowed"
        )

    # 2. Generate unique ID and filename
    video_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]  # .mp4 / .mov
    unique_filename = f"{video_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. Save file to disk (like fs.writeFile in Node)
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # read 1MB at a time
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # 4. Extract video metadata using FFmpeg
    metadata = extract_video_metadata(file_path)

    # 5. Generate thumbnail
    thumbnail_path = generate_thumbnail(file_path, video_id)

    # 6. Save to MongoDB (like new Video({...}).save())
    video = Video(
        filename=file.filename,
        original_path=file_path,
        thumbnail_path=thumbnail_path,
        duration=metadata.get("duration"),
        width=metadata.get("width"),
        height=metadata.get("height"),
        fps=metadata.get("fps"),
        size_mb=metadata.get("size_mb"),
        status="uploaded"
    )
    await video.insert()

    return {
        "message": "Video uploaded successfully",
        "video_id": str(video.id),
        "filename": file.filename,
        "duration": metadata.get("duration"),
        "resolution": f"{metadata.get('width')}x{metadata.get('height')}",
        "thumbnail": thumbnail_path
    }


# ─────────────────────────────────────────
# GET /api/videos/
# Like: router.get('/', async (req, res) => Video.find())
# ─────────────────────────────────────────
@router.get("/")
async def get_all_videos():
    videos = await Video.find().to_list()
    return [
        {
            "id": str(v.id),
            "filename": v.filename,
            "duration": v.duration,
            "resolution": f"{v.width}x{v.height}",
            "thumbnail": v.thumbnail_path,
            "status": v.status,
            "size_mb": v.size_mb,
            "created_at": v.created_at
        }
        for v in videos
    ]


# ─────────────────────────────────────────
# GET /api/videos/:id
# Like: router.get('/:id', async (req, res) => Video.findById(req.params.id))
# ─────────────────────────────────────────
@router.get("/{video_id}")
async def get_video(video_id: str):
    video = await Video.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


# ─────────────────────────────────────────
# DELETE /api/videos/:id
# ─────────────────────────────────────────
@router.delete("/{video_id}")
async def delete_video(video_id: str):
    video = await Video.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Delete file from disk
    if os.path.exists(video.original_path):
        os.remove(video.original_path)

    await video.delete()
    return {"message": "Video deleted successfully"}