# reels-backend/services/smart_crop.py

import ffmpeg
import os


def crop_to_vertical(
    input_path: str,
    output_path: str,
    focal_x: int,
    video_width: int,
    video_height: int
) -> str:
    crop_width = int(video_height * 9 / 16)
    crop_x = focal_x - (crop_width // 2)
    crop_x = max(0, min(crop_x, video_width - crop_width))

    print(f"📐 Cropping: width={crop_width}, x={crop_x}, focal_x={focal_x}")

    try:
        input_stream = ffmpeg.input(input_path)

        # Separate video and audio streams
        video = input_stream.video
        audio = input_stream.audio   # ← keep audio separately

        # Apply crop + scale to video only
        video = video.filter("crop", crop_width, video_height, crop_x, 0)
        video = video.filter("scale", 1080, 1920)

        try:
            # Try with audio first
            (
                ffmpeg
                .output(
                    video,
                    audio,             # ← include audio in output
                    output_path,
                    vcodec="libx264",
                    acodec="aac",
                    video_bitrate="2500k",
                    movflags="faststart",
                    preset="fast"
                )
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error:
            # If audio fails (no audio track) — output video only
            print("⚠️ No audio in source — cropping video only")
            (
                ffmpeg
                .output(
                    video,
                    output_path,
                    vcodec="libx264",
                    video_bitrate="2500k",
                    movflags="faststart",
                    preset="fast"
                )
                .overwrite_output()
                .run(quiet=True)
            )

        print(f"✅ Smart crop complete: {output_path}")
        return output_path

    except ffmpeg.Error as e:
        raise Exception(f"Smart crop failed: {e.stderr.decode()}")