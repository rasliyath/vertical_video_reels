// src/components/ProcessingStatus.jsx
import { useState, useEffect } from "react";
import { getReelStatus } from "../api/reels";

const STAGE_LABELS = {
  pending:    { label: "Waiting in queue...",     color: "#666" },
  trimming:   { label: "✂️ Trimming clip...",      color: "#f0a500" },
  detecting:  { label: "🔍 Detecting subjects...", color: "#f0a500" },
  cropping:   { label: "📐 Smart cropping 9:16...",color: "#f0a500" },
  subtitles:  { label: "💬 Generating subtitles...",color: "#f0a500" },
  headline:   { label: "✍️ Writing headline...",   color: "#f0a500" },
  finalizing: { label: "🎬 Finalizing video...",   color: "#6c63ff" },
  ready:      { label: "✅ Reel is ready!",        color: "#00c853" },
  failed:     { label: "❌ Processing failed",     color: "#ff4d4d" },
};

export default function ProcessingStatus({ reelId, onReady }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!reelId) return;

    // Poll every 3 seconds (like setInterval)
    const interval = setInterval(async () => {
      try {
        const data = await getReelStatus(reelId);
        setStatus(data);

        // Stop polling when done
        if (data.status === "ready" || data.status === "failed") {
          clearInterval(interval);
          if (data.status === "ready") onReady?.(data);
        }
      } catch (err) {
        console.error("Status poll failed", err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [reelId]);

  if (!status) return null;

  const stage = STAGE_LABELS[status.status] || STAGE_LABELS.pending;

  return (
    <div style={{
      background: "#1e1e2e", borderRadius: "8px",
      padding: "12px", marginTop: "10px",
      border: `1px solid ${stage.color}30`
    }}>
      <p style={{ fontSize: "12px", color: stage.color, marginBottom: "8px" }}>
        {stage.label}
      </p>

      {/* Progress Bar */}
      <div style={{
        background: "#333", borderRadius: "4px",
        height: "4px", width: "100%"
      }}>
        <div style={{
          background: stage.color,
          height: "100%",
          width: `${status.processing_percent}%`,
          borderRadius: "4px",
          transition: "width 0.5s ease"
        }} />
      </div>

      <p style={{ fontSize: "11px", color: "#555", marginTop: "6px" }}>
        {status.processing_percent}%
      </p>

      {status.error_message && (
        <p style={{ fontSize: "11px", color: "#ff4d4d", marginTop: "6px" }}>
          {status.error_message}
        </p>
      )}
    </div>
  );
}