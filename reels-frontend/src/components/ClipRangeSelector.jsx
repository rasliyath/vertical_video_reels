// src/components/ClipRangeSelector.jsx
import { useState } from "react";

export default function ClipRangeSelector({ duration, onConfirm, onCancel }) {
  const maxDuration = Math.min(duration || 60, 60); // cap at 60s
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(Math.min(30, maxDuration));

  const clipLength = (end - start).toFixed(1);

  const handleConfirm = () => {
    if (end - start < 5) {
      alert("Clip must be at least 5 seconds");
      return;
    }
    onConfirm({ start, end });
  };

  return (
    <div style={{
      background: "#1e1e2e",
      borderRadius: "10px",
      padding: "16px",
      marginTop: "12px",
      border: "1px solid #333"
    }}>
      <p style={{ fontSize: "13px", color: "#aaa", marginBottom: "12px" }}>
        Select clip range (max 60s)
      </p>

      {/* Start Time */}
      <div style={{ marginBottom: "10px" }}>
        <label style={{ fontSize: "12px", color: "#888", display: "block", marginBottom: "4px" }}>
          Start: {start}s
        </label>
        <input
          type="range" min={0} max={maxDuration - 5}
          value={start}
          onChange={(e) => {
            const val = Number(e.target.value);
            setStart(val);
            if (end <= val + 5) setEnd(Math.min(val + 5, maxDuration));
          }}
          style={{ width: "100%", accentColor: "#6c63ff" }}
        />
      </div>

      {/* End Time */}
      <div style={{ marginBottom: "12px" }}>
        <label style={{ fontSize: "12px", color: "#888", display: "block", marginBottom: "4px" }}>
          End: {end}s
        </label>
        <input
          type="range" min={5} max={maxDuration}
          value={end}
          onChange={(e) => {
            const val = Number(e.target.value);
            setEnd(val);
            if (start >= val - 5) setStart(Math.max(val - 5, 0));
          }}
          style={{ width: "100%", accentColor: "#6c63ff" }}
        />
      </div>

      {/* Clip Info */}
      <p style={{
        fontSize: "12px", color: "#6c63ff",
        marginBottom: "12px", fontWeight: "600"
      }}>
        📎 Clip length: {clipLength}s
      </p>

      {/* Buttons */}
      <div style={{ display: "flex", gap: "8px" }}>
        <button onClick={handleConfirm} style={{
          flex: 1, padding: "8px",
          background: "#6c63ff", color: "#fff",
          border: "none", borderRadius: "6px",
          cursor: "pointer", fontSize: "13px", fontWeight: "600"
        }}>
          ✅ Generate Reel
        </button>
        <button onClick={onCancel} style={{
          padding: "8px 16px",
          background: "#333", color: "#aaa",
          border: "none", borderRadius: "6px",
          cursor: "pointer", fontSize: "13px"
        }}>
          Cancel
        </button>
      </div>
    </div>
  );
}