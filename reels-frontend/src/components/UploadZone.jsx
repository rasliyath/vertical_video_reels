// src/components/UploadZone.jsx
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { uploadVideo } from "../api/videos";

export default function UploadZone({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setProgress(0);

    try {
      const result = await uploadVideo(file, setProgress);
      onUploadSuccess(result);            // notify parent to refresh list
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/*": [".mp4", ".mov", ".avi"] },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div
      {...getRootProps()}
      style={{
        border: `2px dashed ${isDragActive ? "#6c63ff" : "#ddd"}`,
        borderRadius: "12px",
        padding: "30px",
        textAlign: "center",
        cursor: uploading ? "not-allowed" : "pointer",
        background: isDragActive ? "#f0f0ff" : "#fafafa",
        transition: "all 0.2s",
      }}
    >
      <input {...getInputProps()} />

      {uploading ? (
        <div>
          <p style={{ marginBottom: "12px", color: "#666" }}>
            Uploading... {progress}%
          </p>
          {/* Progress Bar */}
          <div style={{
            background: "#e0e0e0", borderRadius: "4px",
            height: "6px", width: "100%", maxWidth: "300px",
            margin: "0 auto"
          }}>
            <div style={{
              background: "#6c63ff", height: "100%",
              width: `${progress}%`, borderRadius: "4px",
              transition: "width 0.3s"
            }} />
          </div>
        </div>
      ) : (
        <div>
          <div style={{ fontSize: "36px", marginBottom: "12px" }}>📤</div>
          <p style={{ fontSize: "15px", color: "#333", marginBottom: "6px", fontWeight: "500" }}>
            {isDragActive ? "Drop video here..." : "Drag & drop a video"}
          </p>
          <p style={{ fontSize: "13px", color: "#888" }}>
            MP4, MOV, AVI — max 500MB
          </p>
        </div>
      )}

      {error && (
        <p style={{ color: "#ff4d4d", marginTop: "12px", fontSize: "13px" }}>
          ⚠️ {error}
        </p>
      )}
    </div>
  );
}
