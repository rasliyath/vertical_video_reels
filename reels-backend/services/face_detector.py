# reels-backend/services/face_detector.py

import cv2
import os
import numpy as np
from ultralytics import YOLO

# YOLOv8 nano model — downloads automatically on first run (~6MB)
# nano = fastest, good enough for detecting people/faces
model = YOLO("yolov8n.pt")

# Classes we care about (from COCO dataset)
# 0 = person, 15 = cat, 16 = dog (expand if needed)
TARGET_CLASSES = [0]


def get_focal_point(video_path: str) -> dict:
    """
    Sample frames from video, detect subjects using YOLOv8
    Return average focal point (x, y) across all detections

    Like finding the "center of attention" in the video
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception(f"Could not open video: {video_path}")

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Sample every 0.5 seconds (not every frame — too slow)
    sample_interval = max(1, int(fps * 0.5))

    focal_points = []
    frame_count = 0

    print(f"🔍 Analyzing {total_frames} frames at {fps}fps...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Only process every Nth frame
        if frame_count % sample_interval == 0:
            detections = detect_subjects_in_frame(frame)

            if detections:
                # Get center X of all detections in this frame
                frame_center_x = np.mean([d["center_x"] for d in detections])
                frame_center_y = np.mean([d["center_y"] for d in detections])
                focal_points.append({
                    "x": frame_center_x,
                    "y": frame_center_y
                })

        frame_count += 1

    cap.release()

    # Calculate final focal point
    if focal_points:
        avg_x = int(np.mean([p["x"] for p in focal_points]))
        avg_y = int(np.mean([p["y"] for p in focal_points]))
        print(f"✅ Subject detected — focal point: ({avg_x}, {avg_y})")
    else:
        # Fallback: use center of frame if nothing detected
        avg_x = width // 2
        avg_y = height // 2
        print(f"⚠️ No subject detected — using center: ({avg_x}, {avg_y})")

    return {
        "focal_x": avg_x,
        "focal_y": avg_y,
        "width": width,
        "height": height,
        "detection_count": len(focal_points)
    }


def detect_subjects_in_frame(frame: np.ndarray) -> list:
    """
    Run YOLOv8 on a single frame
    Returns list of detected subjects with their centers
    """
    try:
        # Run inference — confidence threshold 0.4 (40%)
        results = model(frame, conf=0.4, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])

                # Only care about target classes (people)
                if class_id not in TARGET_CLASSES:
                    continue

                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Calculate center of bounding box
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                confidence = float(box.conf[0])

                detections.append({
                    "class_id": class_id,
                    "center_x": center_x,
                    "center_y": center_y,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

        return detections

    except Exception as e:
        print(f"Frame detection error: {e}")
        return []