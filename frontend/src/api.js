import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Upload & analyze file
export const analyzeFile = (formData) =>
  API.post("/api/analyze/file", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const analyzeContent = (data) =>
  API.post("/api/analyze/content", data);

// Save file
export const saveFile = (formData) =>
  API.post("/api/files/save", formData);

// Get saved files
export const getFiles = () =>
  API.get("/api/files");

// Analyze saved file
export const analyzeSavedFile = (filename) =>
  API.get(`/api/analyze/saved/${filename}`);

export default API;