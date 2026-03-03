// src/components/HeadlineEditor.jsx
import { useState } from "react";
import { updateHeadline, regenerateHeadline } from "../api/reels";

export default function HeadlineEditor({ reel, onUpdate }) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(reel.headline || "");
  const [options, setOptions] = useState(reel.headline_options || []);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    try {
      await updateHeadline(reel.id, text);
      onUpdate?.({ ...reel, headline: text });
      setEditing(false);
    } catch (err) {
      console.error("Failed to save headline", err);
    }
  };

  const handleRegenerate = async () => {
    setLoading(true);
    try {
      const result = await regenerateHeadline(reel.id);
      setOptions(result.headline_options);
      setText(result.headline);
      onUpdate?.({ ...reel, headline: result.headline });
    } catch (err) {
      console.error("Regenerate failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePickOption = async (option) => {
    setText(option);
    await updateHeadline(reel.id, option);
    onUpdate?.({ ...reel, headline: option });
    setEditing(false);
  };

  if (!editing) {
    return (
      <div
        style={styles.headlineWrapper}
        onClick={() => setEditing(true)}
        title="Tap to edit headline"
      >
        <p style={styles.headlineText}>
          {text || "Tap to add headline"}
        </p>
        <span style={styles.editHint}>✏️ tap to edit</span>
      </div>
    );
  }

  return (
    <div style={styles.editorOverlay}>
      <div style={styles.editorBox}>
        <p style={styles.editorLabel}>Edit Headline</p>

        {/* Text Input */}
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={styles.editorInput}
          placeholder="Enter headline..."
          maxLength={80}
          autoFocus
        />

        {/* Character count */}
        <p style={styles.charCount}>{text.length}/80</p>

        {/* AI Options */}
        {options.length > 0 && (
          <div style={styles.optionsSection}>
            <p style={styles.optionsLabel}>AI Suggestions:</p>
            {options.map((opt, i) => (
              <button
                key={i}
                onClick={() => handlePickOption(opt)}
                style={{
                  ...styles.optionBtn,
                  background: opt === text ? "#6c63ff" : "#2a2a2a",
                  color: opt === text ? "#fff" : "#ccc",
                }}
              >
                {opt}
              </button>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div style={styles.editorActions}>
          <button
            onClick={handleRegenerate}
            disabled={loading}
            style={styles.regenBtn}
          >
            {loading ? "⏳" : "🔄"} Regenerate
          </button>
          <button onClick={handleSave} style={styles.saveBtn}>
            ✅ Save
          </button>
          <button
            onClick={() => setEditing(false)}
            style={styles.cancelBtn}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  headlineWrapper: {
    position: "absolute",
    top: "24px",
    left: "16px",
    right: "16px",
    zIndex: 10,
    cursor: "pointer",
    textAlign: "center",
  },
  headlineText: {
    fontSize: "20px",
    fontWeight: "700",
    color: "#fff",
    textShadow: "0 2px 8px rgba(0,0,0,0.8)",
    lineHeight: 1.3,
  },
  editHint: {
    fontSize: "10px",
    color: "rgba(255,255,255,0.4)",
    marginTop: "4px",
    display: "block",
  },
  editorOverlay: {
    position: "absolute",
    inset: 0,
    background: "rgba(0,0,0,0.85)",
    zIndex: 20,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "20px",
  },
  editorBox: {
    width: "100%",
    maxWidth: "360px",
  },
  editorLabel: {
    color: "#aaa",
    fontSize: "12px",
    marginBottom: "8px",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  editorInput: {
    width: "100%",
    padding: "10px 12px",
    background: "#1a1a1a",
    border: "1px solid #6c63ff",
    borderRadius: "8px",
    color: "#fff",
    fontSize: "15px",
    outline: "none",
    boxSizing: "border-box",
  },
  charCount: {
    fontSize: "11px",
    color: "#555",
    textAlign: "right",
    marginTop: "4px",
    marginBottom: "12px",
  },
  optionsSection: {
    marginBottom: "16px",
  },
  optionsLabel: {
    fontSize: "11px",
    color: "#666",
    marginBottom: "8px",
  },
  optionBtn: {
    display: "block",
    width: "100%",
    padding: "8px 12px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "13px",
    marginBottom: "6px",
    textAlign: "left",
  },
  editorActions: {
    display: "flex",
    gap: "8px",
  },
  regenBtn: {
    flex: 1,
    padding: "8px",
    background: "#333",
    color: "#aaa",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "12px",
  },
  saveBtn: {
    flex: 1,
    padding: "8px",
    background: "#6c63ff",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "600",
  },
  cancelBtn: {
    padding: "8px 12px",
    background: "#222",
    color: "#666",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "12px",
  },
};