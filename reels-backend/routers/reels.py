# reels-backend/routers/reels.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from models.reel import Reel
from models.video import Video
from services.reel_service import (
    trim_video,
    detect_focal_point,
    smart_crop_video,
    generate_subtitles,
    generate_headline,
    burn_headline_and_subtitles
)
from datetime import datetime
import os

router = APIRouter()


# ─────────────────────────────────────────
# Request body schema
# ─────────────────────────────────────────
class GenerateReelRequest(BaseModel):
    video_id: str
    start_time: float = 0
    end_time: float = 60
    subtitle_language: str = None  # Optional: en, ml, ta, hi, etc.


# ─────────────────────────────────────────
# BACKGROUND PIPELINE FUNCTION
# This runs in background after API responds
# ─────────────────────────────────────────
async def process_reel_pipeline(
    reel_id: str,
    video_path: str,
    start: float,
    end: float,
    subtitle_language: str = None
):
    """
    Full AI processing pipeline
    Runs in background — API doesn't wait for this
    """

    REELS_DIR = "storage/reels"
    os.makedirs(REELS_DIR, exist_ok=True)

    async def update_status(status: str, percent: int, extra: dict = {}):
        """Helper to update reel progress in MongoDB"""
        reel = await Reel.get(reel_id)
        if reel:
            update_data = {
                "status": status,
                "processing_percent": percent,
                **extra
            }
            await reel.set(update_data)

    try:

        # ── STAGE 1: Trim clip ───────────────────────────
        await update_status("trimming", 10)
        trimmed_path = f"{REELS_DIR}/{reel_id}_trimmed.mp4"
        trim_video(video_path, trimmed_path, start, end)

        # ── STAGE 2: Detect focal point ──────────────────
        await update_status("detecting", 25)
        focal_data = detect_focal_point(trimmed_path)

        # ── STAGE 3: Smart crop 9:16 ─────────────────────
        await update_status("cropping", 40, {
            "focal_x": focal_data["focal_x"],
            "focal_y": focal_data["focal_y"]
        })
        cropped_path = f"{REELS_DIR}/{reel_id}_cropped.mp4"
        smart_crop_video(trimmed_path, cropped_path, focal_data)

        # ── STAGE 4: Generate subtitles ──────────────────
        await update_status("subtitles", 60)
        subtitle_data = generate_subtitles(cropped_path, reel_id, subtitle_language)

        # ── STAGE 5: Generate headline ───────────────────
        await update_status("headline", 75)
        headline_options = generate_headline(subtitle_data["transcript"])
        headline = headline_options[0]

        # ── STAGE 6: Burn headline onto video ────────────
        await update_status("finalizing", 88)
        final_path = f"{REELS_DIR}/{reel_id}_final.mp4"
        burn_headline_and_subtitles(
            cropped_path,
            final_path,
            headline,
            subtitle_data.get("subtitle_path")
        )

        # ── STAGE 7: Save final results to MongoDB ───────
        await update_status("ready", 100, {
            "reel_path": final_path,
            "transcript": subtitle_data["transcript"],
            "subtitle_segments": subtitle_data["segments"],
            "headline": headline,
            "headline_options": headline_options,
            "completed_at": datetime.utcnow()
        })

        # ── Cleanup temp files ────────────────────────────
        for temp in [trimmed_path, cropped_path]:
            if os.path.exists(temp):
                os.remove(temp)

        print(f"✅ Reel {reel_id} completed!")

    except Exception as e:
        print(f"❌ Reel {reel_id} failed: {e}")
        await update_status("failed", 0, {
            "error_message": str(e)
        })


# ─────────────────────────────────────────
# POST /api/reels/generate
# ─────────────────────────────────────────
@router.post("/generate")
async def generate_reel(
    body: GenerateReelRequest,
    background_tasks: BackgroundTasks
):
    # 1. Check video exists
    video = await Video.get(body.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # 2. Validate clip range
    if body.end_time - body.start_time < 5:
        raise HTTPException(
            status_code=400,
            detail="Clip must be at least 5 seconds"
        )
    if body.end_time - body.start_time > 60:
        raise HTTPException(
            status_code=400,
            detail="Clip cannot exceed 60 seconds"
        )

    # 3. Create reel record in MongoDB
    reel = Reel(
        video_id=body.video_id,
        start_time=body.start_time,
        end_time=body.end_time,
        status="pending",
        processing_percent=0
    )
    await reel.insert()

    # 4. Run pipeline in background (no Redis/Celery needed)
    background_tasks.add_task(
        process_reel_pipeline,
        str(reel.id),
        video.original_path,
        body.start_time,
        body.end_time,
        body.subtitle_language
    )

    # 5. Return immediately — don't wait for processing
    return {
        "message": "Reel generation started",
        "reel_id": str(reel.id),
        "status": "pending"
    }


# ─────────────────────────────────────────
# GET /api/reels/
# ─────────────────────────────────────────
@router.get("/")
async def get_all_reels():
    reels = await Reel.find().to_list()
    return [
        {
            "id": str(r.id),
            "video_id": r.video_id,
            "status": r.status,
            "processing_percent": r.processing_percent,
            "reel_path": r.reel_path,
            "headline": r.headline,
            "headline_options": r.headline_options,
            "duration": r.end_time - r.start_time,
            "created_at": r.created_at
        }
        for r in reels
    ]


# ─────────────────────────────────────────
# GET /api/reels/:id/status
# Frontend polls this every 3 seconds
# ─────────────────────────────────────────
@router.get("/{reel_id}/status")
async def get_reel_status(reel_id: str):
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    return {
        "reel_id": str(reel.id),
        "status": reel.status,
        "processing_percent": reel.processing_percent,
        "error_message": reel.error_message,
        "reel_path": reel.reel_path,
        "headline": reel.headline,
        "headline_options": reel.headline_options
    }


# ─────────────────────────────────────────
# PATCH /api/reels/:id/headline
# User edits headline after generation
# ─────────────────────────────────────────
@router.patch("/{reel_id}/headline")
async def update_headline(reel_id: str, body: dict):
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    await reel.set({"headline": body.get("headline")})
    return {
        "message": "Headline updated",
        "headline": body.get("headline")
    }


# ─────────────────────────────────────────
# DELETE /api/reels/:id
# ─────────────────────────────────────────
@router.delete("/{reel_id}")
async def delete_reel(reel_id: str):
    reel = await Reel.get(reel_id)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    # Delete file from disk
    if reel.reel_path and os.path.exists(reel.reel_path):
        os.remove(reel.reel_path)

    await reel.delete()
    return {"message": "Reel deleted"}