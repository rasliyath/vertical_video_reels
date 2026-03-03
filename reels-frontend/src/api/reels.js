// src/api/reels.js
import API from "./axios";

export const getAllReels = async () => {
  const res = await API.get("/reels/");
  return res.data;
};

export const getReelStatus = async (reelId) => {
  const res = await API.get(`/reels/${reelId}/status`);
  return res.data;
};

export const updateHeadline = async (reelId, headline) => {
  const res = await API.patch(`/reels/${reelId}/headline`, { headline });
  return res.data;
};

export const regenerateHeadline = async (reelId) => {
  const res = await API.post(`/reels/${reelId}/regenerate-headline`);
  return res.data;
};

export const deleteReel = async (reelId) => {
  const res = await API.delete(`/reels/${reelId}`);
  return res.data;
};