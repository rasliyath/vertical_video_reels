// src/api/videos.js
import API from "./axios";

export const uploadVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await API.post("/videos/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      const percent = Math.round((e.loaded * 100) / e.total);
      onProgress(percent);
    },
  });
  return res.data;
};

export const getAllVideos = async () => {
  const res = await API.get("/videos/");
  return res.data;
};

export const deleteVideo = async (id) => {
  const res = await API.delete(`/videos/${id}`);
  return res.data;
};