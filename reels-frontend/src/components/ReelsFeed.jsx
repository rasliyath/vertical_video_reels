// src/pages/ReelsFeed.jsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getAllReels } from "../api/reels";
import SwipeFeed from "../components/SwipeFeed";

export default function ReelsFeed() {
  const [reels, setReels] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchReels();
  }, []);

  const fetchReels = async () => {
    try {
      const data = await getAllReels();
      // Only show ready reels in feed
      const readyReels = data.filter((r) => r.status === "ready");
      setReels(readyReels);
    } catch (err) {
      console.error("Failed to fetch reels", err);
    } finally {
      setLoading(false);
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
        background: "#0f0f0f", color: "#666"
      }}>
        Loading reels...
      </div>
    );
  }

  return (
    <div style={{ position: "relative" }}>

      {/* Back to Dashboard Button */}
      <button
        onClick={() => navigate("/")}
        style={{
          position: "fixed",
          top: "16px",
          left: "16px",
          zIndex: 100,
          background: "rgba(0,0,0,0.6)",
          color: "#fff",
          border: "1px solid #333",
          borderRadius: "8px",
          padding: "8px 14px",
          cursor: "pointer",
          fontSize: "13px",
          backdropFilter: "blur(8px)"
        }}
      >
        ← Dashboard
      </button>

      <SwipeFeed
        reels={reels}
        onHeadlineUpdate={handleHeadlineUpdate}
      />
    </div>
  );
}