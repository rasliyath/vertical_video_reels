// reels-frontend/src/api/axios.js
import axios from "axios";

// Auto-detect base URL — works for localhost AND ngrok
export const BASE_URL = window.location.origin;

const API = axios.create({
  baseURL: `${BASE_URL}/api`,
});

export default API;