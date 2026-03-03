# reels-backend/services/reel_service.py

import os
import ffmpeg

UPLOAD_DIR = "storage/uploads"
REELS_DIR = "storage/reels"
os.makedirs(REELS_DIR, exist_ok=True)


def trim_video(input_path: str, output_path: str, start: float, end: float):
    try:
        (
            ffmpeg
            .input(input_path, ss=start, to=end)
            .output(output_path, c="copy")
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except Exception as e:
        raise Exception(f"Trim failed: {e}")


def detect_focal_point(video_path: str) -> dict:
    # Placeholder — real YOLOv8 detection coming in Step 6
    try:
        probe = ffmpeg.probe(video_path)
        video_stream = next(
            s for s in probe["streams"] if s["codec_type"] == "video"
        )
        width = int(video_stream["width"])
        height = int(video_stream["height"])
        return {
            "focal_x": width // 2,
            "focal_y": height // 2,
            "width": width,
            "height": height
        }
    except Exception as e:
        raise Exception(f"Detection failed: {e}")


def smart_crop_video(input_path: str, output_path: str, focal_data: dict) -> str:
    # Placeholder — real smart crop coming in Step 6
    try:
        width = focal_data["width"]
        height = focal_data["height"]
        focal_x = focal_data["focal_x"]

        crop_width = int(height * 9 / 16)
        crop_x = max(0, min(focal_x - crop_width // 2, width - crop_width))

        (
            ffmpeg
            .input(input_path)
            .filter("crop", crop_width, height, crop_x, 0)
            .filter("scale", 1080, 1920)
            .output(output_path, vcodec="libx264", acodec="aac")
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except Exception as e:
        raise Exception(f"Crop failed: {e}")


def generate_subtitles(video_path: str, reel_id: str) -> dict:
    # Placeholder — real Whisper coming in Step 7
    return {
        "transcript": "Subtitle generation coming in Step 7",
        "subtitle_path": None,
        "segments": []
    }


def generate_headline(transcript: str) -> list:
    # Placeholder — real AI headline coming in Step 8
    return [
        "AI Headline Coming Soon",
        "Your Story Starts Here",
        "Watch This Now"
    ]


def burn_headline_and_subtitles(
    input_path: str,
    output_path: str,
    headline: str,
    subtitle_path: str = None
) -> str:
    try:
        video = ffmpeg.input(input_path)
        video = video.filter(
            "drawtext",
            text=headline,
            fontsize=36,
            fontcolor="white",
            x="(w-text_w)/2",
            y=80,
            box=1,
            boxcolor="black@0.5",
            boxborderw=8
        )
        (
            ffmpeg
            .output(video, output_path,
                    vcodec="libx264",
                    acodec="aac",
                    movflags="faststart")
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except Exception as e:
        raise Exception(f"Headline burn failed: {e}")