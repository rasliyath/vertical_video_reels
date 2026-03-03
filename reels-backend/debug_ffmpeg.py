# reels-backend/debug_ffmpeg.py

import subprocess
import os

# ← Paste your actual video path here
video_path = r"storage\uploads\your_actual_video_file.mp4"
audio_path = r"storage\test_audio.wav"

video_path = os.path.abspath(video_path)
audio_path = os.path.abspath(audio_path)

print(f"Video exists: {os.path.exists(video_path)}")
print(f"Video path: {video_path}")

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

result = subprocess.run(cmd, capture_output=True, text=True)

print(f"Return code: {result.returncode}")
print(f"STDERR:\n{result.stderr}")
print(f"Audio created: {os.path.exists(audio_path)}")