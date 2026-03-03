// src/pages/Dashboard.jsx
import { useState, useEffect } from "react";
import { getAllVideos, deleteVideo } from "../api/videos";
import UploadZone from "../components/UploadZone";
import VideoCard from "../components/VideoCard";
import SwipeFeed from "../components/SwipeFeed";
import API from "../api/axios";
import { getAllReels } from "../api/reels";

export default function Dashboard() {
  const [videos, setVideos] = useState([]);
  const [reels, setReels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  // Fetch all videos and reels on mount
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [videosData, reelsData] = await Promise.all([
        getAllVideos(),
        getAllReels()
      ]);
      setVideos(videosData);
      // Only show ready reels
      setReels(reelsData.filter((r) => r.status === "ready"));
    } catch (err) {
      console.error("Failed to fetch data", err);
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (msg, type = "success") => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Called after successful upload
  const handleUploadSuccess = (result) => {
    showNotification(`✅ "${result.filename}" uploaded!`);
    fetchData(); // refresh list
  };

  // Called when user clicks delete
  const handleDelete = async (videoId) => {
    try {
      await deleteVideo(videoId);
      setVideos((prev) => prev.filter((v) => v.id !== videoId));
      showNotification("🗑 Video deleted");
    } catch (err) {
      showNotification("Delete failed", "error");
    }
  };

  // Called when user confirms reel generation
  const handleGenerateReel = async (videoId, range, subtitleLang, onStarted) => {
    try {
      const result = await API.post("/reels/generate", {
        video_id: videoId,
        start_time: range.start,
        end_time: range.end,
        subtitle_language: subtitleLang,
      });
      showNotification("🎬 Reel generation started!");
      const newReelId = result.data.reel_id;
      onStarted?.(newReelId); // pass reel_id back to card
      
      // Poll for reel status and update immediately when ready
      const pollReelStatus = async () => {
        try {
          const statusRes = await API.get(`/reels/${newReelId}/status`);
          const status = statusRes.data;
          
          if (status.status === "ready") {
            // Reel is ready, refresh the list
            const reelsRes = await getAllReels();
            setReels(reelsRes.filter((r) => r.status === "ready"));
            showNotification("✅ Reel ready!");
          } else if (status.status === "failed") {
            showNotification("❌ Reel generation failed", "error");
          } else {
            // Still processing, continue polling
            setTimeout(pollReelStatus, 2000);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      };
      
      // Start polling
      setTimeout(pollReelStatus, 3000);
      
    } catch (err) {
      showNotification("Failed to start reel generation", "error");
    }
  };

  const handleHeadlineUpdate = (updatedReel) => {
    setReels((prev) =>
      prev.map((r) => (r.id === updatedReel.id ? updatedReel : r))
    );
  };

  if (loading) {
    return (
      <div style={{
        height: "100vh", display: "flex",
        alignItems: "center", justifyContent: "center",
        background: "#f5f5f5", color: "#666"
      }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: "100vh", 
      background: "#f5f5f5",
      padding: "24px"
    }}>

      {/* Notification Toast */}
      {notification && (
        <div style={{
          position: "fixed", top: "24px", right: "24px",
          background: notification.type === "error" ? "#ff4d4d" : "#6c63ff",
          color: "#fff", padding: "12px 20px",
          borderRadius: "8px", fontSize: "14px",
          zIndex: 1000, boxShadow: "0 4px 20px rgba(0,0,0,0.3)"
        }}>
          {notification.msg}
        </div>
      )}

      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "700", color: "#1a1a1a", marginBottom: "6px" }}>
          🎬 Reels Studio
        </h1>
        <p style={{ color: "#666", fontSize: "14px" }}>
          Upload landscape videos and convert them to vertical reels
        </p>
      </div>

      {/* Two-Column Layout */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1100px 1fr",
        gap: "24px",
        alignItems: "start"
      }}>

        {/* LEFT PANEL: Reels Studio (Upload + Videos) */}
        <div style={{
          background: "#fff",
          borderRadius: "12px",
          padding: "20px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)"
        }}>
          {/* Upload Zone */}
          <UploadZone onUploadSuccess={handleUploadSuccess} />

          {/* Video List */}
          <div style={{ marginTop: "20px" }}>
            <h2 style={{ fontSize: "16px", color: "#333", marginBottom: "16px" }}>
              Your Videos ({videos.length})
            </h2>

            {videos.length === 0 ? (
              <div style={{
                textAlign: "center", color: "#999",
                padding: "40px 20px", border: "2px dashed #e0e0e0",
                borderRadius: "12px"
              }}>
                <div style={{ fontSize: "40px", marginBottom: "12px" }}>📭</div>
                <p>No videos yet. Upload one above!</p>
              </div>
            ) : (
              <div style={{ 
                display: "grid", 
                gridTemplateColumns: "repeat(3, 1fr)", 
                gap: "16px" 
              }}>
                {videos.map((video) => (
                  <VideoCard
                    key={video.id}
                    video={video}
                    onDelete={handleDelete}
                    onGenerateReel={handleGenerateReel}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANEL: Generated Reels Feed */}
        <div style={{
          background: "#fff",
          borderRadius: "12px",
          padding: "20px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          maxHeight: "calc(100vh - 140px)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column"
        }}>
          <h2 style={{ fontSize: "18px", color: "#333", marginBottom: "16px" }}>
            Generated Reels ({reels.length})
          </h2>

          {reels.length === 0 ? (
            <div style={{
              textAlign: "center", color: "#999",
              padding: "60px 20px", border: "2px dashed #e0e0e0",
              borderRadius: "12px"
            }}>
              <div style={{ fontSize: "48px", marginBottom: "12px" }}>🎬</div>
              <p>No reels generated yet.</p>
              <p style={{ fontSize: "13px", marginTop: "8px" }}>
                Upload a video and click "Make Reel" to get started!
              </p>
            </div>
          ) : (
            <SwipeFeed
              reels={reels}
              onHeadlineUpdate={handleHeadlineUpdate}
            />
          )}
        </div>

      </div>
    </div>
  );
}
