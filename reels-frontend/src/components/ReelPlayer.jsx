// src/components/ReelPlayer.jsx

import { useRef, useEffect, useState } from "react";
import HeadlineEditor from "./HeadlineEditor";

//const BASE_URL = "http://localhost:8000";
import { BASE_URL } from "../api/axios";

export default function ReelPlayer({ reel, isActive, currentIndex = 0, totalReels = 1, onHeadlineUpdate }) {
  const videoRef = useRef(null);
  const [muted, setMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Set muted via ref on first render
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = false;
    }
  }, []);

  // Auto play/pause
  useEffect(() => {
    if (!videoRef.current) return;
    if (isActive) {
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
      setIsPlaying(false);
      setProgress(0);
    }
  }, [isActive]);

  // Track video progress
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const updateProgress = () => {
      if (video.duration) {
        const percent = (video.currentTime / video.duration) * 100;
        setProgress(percent);
      }
    };

    const handleEnded = () => {
      // Loop the video
      video.currentTime = 0;
      video.play().catch(() => {});
    };

    video.addEventListener("timeupdate", updateProgress);
    video.addEventListener("ended", handleEnded);

    return () => {
      video.removeEventListener("timeupdate", updateProgress);
      video.removeEventListener("ended", handleEnded);
    };
  }, [isActive]);

  const toggleMute = (e) => {
    e.stopPropagation();
    const newMuted = !muted;
    setMuted(newMuted);
    if (videoRef.current) {
      videoRef.current.muted = newMuted;
    }
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (videoRef.current.paused) {
        videoRef.current.play();
        setIsPlaying(true);
      } else {
        videoRef.current.pause();
        setIsPlaying(false);
      }
    }
  };

  if (!reel.reel_path) {
    return (
      <div style={styles.emptyContainer}>
        <p style={{ color: "#666" }}>Processing...</p>
      </div>
    );
  }

const videoUrl = `${BASE_URL}/${reel.reel_path.replace(/\\/g, "/")}`

  return (
    <div style={styles.playerContainer}>
      {/* Progress dots at top */}
      <div style={styles.progressContainer}>
        {Array.from({ length: totalReels }).map((_, i) => (
          <div key={i} style={styles.progressTrack}>
            <div 
              style={{
                ...styles.progressFill,
                width: i < currentIndex ? '100%' : (i === currentIndex ? `${progress}%` : '0%'),
              }} 
            />
          </div>
        ))}
      </div>

      <video
        ref={videoRef}
        src={videoUrl}
        style={styles.video}
        loop
        playsInline
        onClick={togglePlay}
      />

      <div style={styles.gradientTop} />
      <div style={styles.gradientBottom} />

      <HeadlineEditor reel={reel} onUpdate={onHeadlineUpdate} />

      <div style={styles.bottomInfo}>
        <p style={styles.duration}>🎬 {Math.round(reel.duration || 0)}s</p>
      </div>

      {/* Play/Pause indicator */}
      {!isPlaying && (
        <div style={styles.playOverlay}>
          <div style={styles.playButton}>▶</div>
        </div>
      )}
    </div>
  );
}

const styles = {
  playerContainer: {
    position: "relative",
    width: "100%",
    height: "100%",
    background: "#000",
    overflow: "hidden",
  },
  progressContainer: {
    position: "absolute",
    top: "12px",
    left: "12px",
    right: "12px",
    display: "flex",
    gap: "4px",
    zIndex: 20,
  },
  progressTrack: {
    flex: 1,
    height: "3px",
    background: "rgba(255,255,255,0.3)",
    borderRadius: "2px",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "#fff",
    borderRadius: "2px",
    transition: "width 0.1s linear",
  },
  video: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    cursor: "pointer",
  },
  gradientTop: {
    position: "absolute",
    top: 0, left: 0, right: 0,
    height: "120px",
    background: "linear-gradient(to bottom, rgba(0,0,0,0.6), transparent)",
    pointerEvents: "none",
  },
  gradientBottom: {
    position: "absolute",
    bottom: 0, left: 0, right: 0,
    height: "160px",
    background: "linear-gradient(to top, rgba(0,0,0,0.7), transparent)",
    pointerEvents: "none",
  },
  bottomInfo: {
    position: "absolute",
    bottom: "24px",
    left: "16px",
    zIndex: 10,
  },
  duration: {
    color: "rgba(255,255,255,0.7)",
    fontSize: "12px",
  },
  playOverlay: {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    zIndex: 15,
  },
  playButton: {
    width: "60px",
    height: "60px",
    background: "rgba(0,0,0,0.6)",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    fontSize: "24px",
    border: "2px solid #fff",
  },
  emptyContainer: {
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#111",
  },
};
