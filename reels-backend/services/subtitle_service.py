# reels-backend/services/subtitle_service.py

import whisper
import ffmpeg
import os
import subprocess 
import re

REELS_DIR = "storage/reels"
SUBTITLES_DIR = "storage/subtitles"
os.makedirs(SUBTITLES_DIR, exist_ok=True)


# Load Whisper model once at startup (not on every request)
# medium model = much better for Malayalam/Tamil vs base model
# Options: tiny | base | small | medium | large
# tiny = fastest, large = most accurate but slow
print("⏳ Loading Whisper model...")
whisper_model = whisper.load_model("medium")
print("✅ Whisper model loaded!")


def extract_audio(video_path: str, audio_path: str) -> str:
    try:
        video_path = os.path.abspath(video_path)
        audio_path = os.path.abspath(audio_path)

        print(f"📂 Input video: {video_path}")
        print(f"📂 Output audio: {audio_path}")
        print(f"📂 Video exists: {os.path.exists(video_path)}")

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",
            "-y",
            audio_path
        ]

        print(f"🔧 Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        # Print FULL error output
        print(f"📋 Return code: {result.returncode}")
        print(f"📋 STDOUT: {result.stdout}")
        print(f"📋 STDERR: {result.stderr}")

        if result.returncode != 0:
            raise Exception(f"FFmpeg failed with code {result.returncode}: {result.stderr}")

        if not os.path.exists(audio_path):
            raise Exception("Audio file was not created after FFmpeg ran")

        print(f"✅ Audio extracted successfully")
        return audio_path

    except Exception as e:
        raise Exception(f"Audio extraction failed: {e}")

def transcribe_audio(audio_path: str, language: str = None) -> dict:
    try:
        audio_path = os.path.abspath(audio_path)
        print(f"🎙️ Transcribing: {audio_path}")

        # Always use Whisper to detect language — don't trust video metadata
        audio_data = whisper.load_audio(audio_path)
        audio_trimmed = whisper.pad_or_trim(audio_data)
        mel = whisper.log_mel_spectrogram(audio_trimmed).to(whisper_model.device)
        _, probs = whisper_model.detect_language(mel)

        # Get top detected language
        detected_lang = max(probs, key=probs.get)
        print(f"🌐 Language probs → {', '.join([f'{k}:{v:.3f}' for k,v in sorted(probs.items(), key=lambda x: -x[1])[:5]])}")
        print(f"🌐 Detected language: {detected_lang}")

        # If user specified a language, use it; otherwise use auto-detected
        final_language = language if language else detected_lang
        print(f"🎯 Final language for transcription: {final_language}")

        result = whisper_model.transcribe(
            audio_path,
            task="transcribe",
            language=final_language,
            verbose=False,
            word_timestamps=False,
            fp16=False,
        )

        print(f"✅ Transcription done in [{final_language}]: {len(result['segments'])} segments")
        return result

    except Exception as e:
        raise Exception(f"Transcription failed: {e}")


def format_srt_time(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format
    Example: 65.5 → 00:01:05,500
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_srt_file(segments: list, srt_path: str) -> str:
    try:
        srt_path = os.path.abspath(srt_path)

        # Find offset — if first subtitle doesn't start at 0
        # adjust all timestamps accordingly
        offset = 0.0
        if segments and segments[0]["start"] > 0.5:
            offset = 0.0   # keep as-is, Whisper timing is usually correct

        with open(srt_path, "w", encoding="utf-8") as f:
            valid_index = 1
            for segment in segments:
                start = max(0, segment["start"] - offset)
                end = max(0, segment["end"] - offset)
                text = segment["text"].strip()

                if not text:
                    continue

                f.write(f"{valid_index}\n")
                f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
                f.write(f"{text}\n\n")
                valid_index += 1

        print(f"✅ SRT file created: {srt_path}")
        return srt_path

    except Exception as e:
        raise Exception(f"SRT creation failed: {e}")


def burn_subtitles_to_video(
    input_path: str,
    output_path: str,
    srt_path: str
) -> str:
    try:
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        srt_path = os.path.abspath(srt_path)

        srt_escaped = srt_path.replace("\\", "/")
        drive, rest = os.path.splitdrive(srt_escaped)
        drive_escaped = drive.replace(":", "\\:")
        srt_final = drive_escaped + rest

        vf_filter = (
            f"subtitles='{srt_final}':force_style="
            "'FontName=Arial,FontSize=16,"
            "PrimaryColour=&HFFFFFF,"
            "OutlineColour=&H000000,"
            "Outline=2,Bold=1,"
            "Alignment=2,MarginV=40'"
        )

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", vf_filter,
            "-vcodec", "libx264",
            "-acodec", "copy",        # ← preserve audio
            "-movflags", "faststart",
            "-y",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"⚠️ Subtitle burn failed — copying without subtitles")
            import shutil
            shutil.copy(input_path, output_path)

        print(f"✅ Subtitles burned with audio preserved")
        return output_path

    except Exception as e:
        raise Exception(f"Subtitle burn failed: {e}")

def check_has_audio(video_path: str) -> bool:
    """Check if video has an audio stream before extracting"""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-select_streams", "a",   # only audio streams
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    import json
    try:
        data = json.loads(result.stdout)
        return len(data.get("streams", [])) > 0
    except Exception:
        return False


def detect_video_language(video_path: str) -> str:
    """
    Detect language from video metadata using ffprobe
    Returns language code (e.g., 'eng', 'mal', 'tam') or None if not found
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "a",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        import json
        data = json.loads(result.stdout)
        
        for stream in data.get("streams", []):
            # Check for language tag in stream metadata
            tags = stream.get("tags", {})
            language = tags.get("language") or tags.get("LANGUAGE")
            if language:
                # Map common language codes to Whisper format
                lang_map = {
                    "eng": "en",
                    "mal": "ml", 
                    "tam": "ta",
                    "hin": "hi",
                    "kan": "kn",
                    "tel": "te",
                    "ben": "bn",
                    "mar": "mr",
                    "guj": "gu",
                    "pol": "pl",
                }
                return lang_map.get(language.lower(), language.lower())
        
        print("⚠️ No language metadata found in video - will use Whisper auto-detection")
        return None
        
    except Exception as e:
        print(f"⚠️ Language detection failed: {e}")
        return None


def generate_subtitles_for_reel(video_path: str, reel_id: str, subtitle_language: str = None) -> dict:
    audio_path = os.path.abspath(f"{SUBTITLES_DIR}/{reel_id}_audio.wav")
    srt_path = os.path.abspath(f"{SUBTITLES_DIR}/{reel_id}.srt")

    try:
        if not check_has_audio(video_path):
            print("⚠️ No audio — skipping subtitles")
            return {"transcript": "", "segments": [], "subtitle_path": None}

        # Use user-specified language, or let Whisper auto-detect
        extract_audio(video_path, audio_path)
        result = transcribe_audio(audio_path, subtitle_language)
        create_srt_file(result["segments"], srt_path)

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {
            "transcript": result["text"].strip(),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip()
                }
                for seg in result["segments"]
            ],
            "subtitle_path": srt_path
        }

    except Exception as e:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise Exception(f"Subtitle generation failed: {e}")