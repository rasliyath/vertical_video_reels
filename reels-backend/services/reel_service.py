# reels-backend/services/reel_service.py

import os
import ffmpeg
from services.face_detector import get_focal_point
from services.smart_crop import crop_to_vertical
from services.subtitle_service import (       # ← ADD THIS IMPORT
    generate_subtitles_for_reel,
    burn_subtitles_to_video
)

REELS_DIR = "storage/reels"
os.makedirs(REELS_DIR, exist_ok=True)


def trim_video(input_path: str, output_path: str, start: float, end: float):
    try:
        input_stream = ffmpeg.input(input_path, ss=start, to=end)

        try:
            # Try with audio
            (
                ffmpeg
                .output(
                    input_stream.video,
                    input_stream.audio,
                    output_path,
                    c="copy"
                )
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error:
            # No audio track — trim video only
            print("⚠️ No audio in source — trimming video only")
            (
                ffmpeg
                .input(input_path, ss=start, to=end)
                .output(output_path, c="copy", an=None)
                .overwrite_output()
                .run(quiet=True)
            )

        print(f"✅ Trimmed: {start}s → {end}s")
        return output_path

    except Exception as e:
        raise Exception(f"Trim failed: {e}")

def detect_focal_point(video_path: str) -> dict:
    print("🔍 Running subject detection...")
    return get_focal_point(video_path)


def smart_crop_video(input_path: str, output_path: str, focal_data: dict) -> str:
    print("📐 Running smart crop...")
    return crop_to_vertical(
        input_path=input_path,
        output_path=output_path,
        focal_x=focal_data["focal_x"],
        video_width=focal_data["width"],
        video_height=focal_data["height"]
    )


def generate_subtitles(video_path: str, reel_id: str, subtitle_language: str = None) -> dict:
    """
    REAL implementation — uses Whisper
    Replaces placeholder from before
    """
    print("🎙️ Generating subtitles with Whisper...")
    return generate_subtitles_for_reel(video_path, reel_id, subtitle_language)


def generate_headline(transcript: str) -> list:
    """
    Generate catchy headlines from transcript using Ollama (local LLM)
    """
    try:
        import ollama
        
        if not transcript or len(transcript.strip()) < 10:
            return ["AI Headline Coming Soon", "Your Story Starts Here", "Watch This Now"]
        
        # Create prompt for headline generation
        prompt = f"""Generate 3 short, catchy social media headlines (5-10 words each) 
based on this video transcript. Make them engaging and attention-grabbing.

Transcript:
{transcript[:500]}...

Return only the headlines, one per line, no numbering or extra text:"""

        response = ollama.generate(
            model="llama3.1",  # Available Ollama model (8B parameters)
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 100
            }
        )
        
        # Parse response into list
        headlines = [line.strip() for line in response['response'].strip().split('\n') if line.strip()]
        
        # Ensure we have 3 headlines
        while len(headlines) < 3:
            headlines.append(f"Watch This Video #{len(headlines)+1}")
        
        return headlines[:3]
        
    except Exception as e:
        print(f"⚠️ Headline generation failed: {e}")
        return ["AI Headline Coming Soon", "Your Story Starts Here", "Watch This Now"]


def burn_headline_and_subtitles(
    input_path: str,
    output_path: str,
    headline: str,
    subtitle_path: str = None
) -> str:
    import subprocess

    try:
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)

        # Step 1: Burn subtitles if available
        if subtitle_path and os.path.exists(subtitle_path):
            subtitled_path = output_path.replace("_final.mp4", "_subtitled.mp4")
            subtitled_path = os.path.abspath(subtitled_path)
            burn_subtitles_to_video(input_path, subtitled_path, subtitle_path)
            input_for_headline = subtitled_path
        else:
            input_for_headline = input_path

        input_for_headline = os.path.abspath(input_for_headline)

        # Escape headline text for FFmpeg
        safe_headline = headline.replace("'", "\\'").replace(":", "\\:")

        # Step 2: Burn headline — explicitly copy audio stream
        cmd = [
            "ffmpeg",
            "-i", input_for_headline,
            "-vf", (
                f"drawtext=text='{safe_headline}':"
                "fontsize=36:"
                "fontcolor=white:"
                "x=(w-text_w)/2:"
                "y=80:"
                "box=1:"
                "boxcolor=black@0.5:"
                "boxborderw=8"
            ),
            "-vcodec", "libx264",
            "-acodec", "copy",        # ← copy audio as-is (don't re-encode)
            "-movflags", "faststart",
            "-y",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        print(f"📋 Headline burn return code: {result.returncode}")

        if result.returncode != 0:
            print(f"⚠️ Headline burn stderr: {result.stderr[-500:]}")

            # Fallback — try without drawtext (just copy with audio)
            cmd_fallback = [
                "ffmpeg",
                "-i", input_for_headline,
                "-vcodec", "copy",
                "-acodec", "copy",
                "-movflags", "faststart",
                "-y",
                output_path
            ]
            subprocess.run(cmd_fallback, capture_output=True)

        # Cleanup temp subtitled file
        if subtitle_path and input_for_headline != input_path:
            if os.path.exists(input_for_headline):
                os.remove(input_for_headline)

        print(f"✅ Headline + audio burned successfully")
        return output_path

    except Exception as e:
        raise Exception(f"Burn failed: {e}")