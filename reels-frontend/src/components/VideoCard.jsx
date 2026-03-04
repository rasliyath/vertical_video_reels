// src/components/VideoCard.jsx
import ClipRangeSelector from "./ClipRangeSelector";
import ProcessingStatus from "./ProcessingStatus";
import { useState } from "react";
import { BASE_URL } from "../api/axios";

export default function VideoCard({ video, onDelete, onGenerateReel }) {
  const [reelToggle, setReelToggle] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [activeReelId, setActiveReelId] = useState(null);
  const [subtitleLang, setSubtitleLang] = useState("");

  const handleDelete = async () => {
    if (!confirm("Delete this video?")) return;
    setDeleting(true);
    await onDelete(video.id);
  };

const handleConfirmReel = (range) => {
  setReelToggle(false);
  onGenerateReel(video.id, range, subtitleLang, (reelId) => {
    setActiveReelId(reelId);    // ← store reel id to show progress
  });
};

  const formatDuration = (sec) => {
    if (!sec) return "Unknown";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "12px",
        overflow: "hidden",
        border: "1px solid #e0e0e0",
        opacity: deleting ? 0.5 : 1,
        transition: "opacity 0.2s",
      }}
    >
      {/* Thumbnail */}
      <div
        style={{
          position: "relative",
          aspectRatio: "16/9",
          background: "#f0f0f0",
        }}
      >
        {video.thumbnail ? (
          <img
            src={`${BASE_URL}/${video.thumbnail}`}
            alt={video.filename}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "32px",
            }}
          >
            🎬
          </div>
        )}

        {/* Duration Badge */}
        <span
          style={{
            position: "absolute",
            bottom: "8px",
            right: "8px",
            background: "rgba(0,0,0,0.7)",
            color: "#fff",
            fontSize: "11px",
            padding: "2px 6px",
            borderRadius: "4px",
          }}
        >
          {formatDuration(video.duration)}
        </span>
      </div>

      {/* Info */}
      <div style={{ padding: "12px" }}>
        <p
          style={{
            fontSize: "13px",
            fontWeight: "600",
            color: "#1a1a1a",
            marginBottom: "4px",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {video.filename}
        </p>
        <p style={{ fontSize: "11px", color: "#666", marginBottom: "12px" }}>
          {video.resolution} • {video.size_mb}MB
        </p>

        {/* Action Buttons */}
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          {/* Generate Reel Toggle */}
          <button
            onClick={() => setReelToggle(!reelToggle)}
            style={{
              flex: 1,
              padding: "8px",
              background: reelToggle ? "#6c63ff" : "#f0f0f0",
              color: reelToggle ? "#fff" : "#333",
              border: "1px solid #ddd",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "12px",
              fontWeight: "600",
              transition: "all 0.2s",
            }}
          >
            {reelToggle ? "✦ Making Reel..." : "⚡ Make Reel"}
          </button>

          {/* Delete */}
          <button
            onClick={handleDelete}
            disabled={deleting}
            style={{
              padding: "8px 10px",
              background: "#f0f0f0",
              color: "#ff4d4d",
              border: "1px solid #ddd",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "12px",
            }}
          >
            🗑
          </button>
        </div>

        {/* Clip Range Selector — shows when toggle is ON */}
        {reelToggle && (
          <>
            {/* Language Selection - commented out - using auto-detect
            <div style={{ marginTop: "12px" }}>
              <label style={{ fontSize: "11px", color: "#666", display: "block", marginBottom: "6px" }}>
                Subtitle Language
              </label>
              <select
                value={subtitleLang}
                onChange={(e) => setSubtitleLang(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px",
                  background: "#fff",
                  color: "#333",
                  border: "1px solid #ddd",
                  borderRadius: "6px",
                  fontSize: "12px",
                  cursor: "pointer",
                }}
              >
                <option value="">Auto-detect</option>
                <option value="ml">Malayalam (മലയാളം)</option>
                <option value="en">English</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="te">Telugu (తెలుగు)</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
              </select>
            </div>
            */}
            <ClipRangeSelector
              duration={video.duration}
              onConfirm={handleConfirmReel}
              onCancel={() => setReelToggle(false)}
            />
          </>
        )}
        {activeReelId && (
          <ProcessingStatus
            reelId={activeReelId}
            onReady={() => setActiveReelId(null)}
          />
        )}
      </div>
    </div>
  );
}