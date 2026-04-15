// frontend/src/services/wrapperApi.js
// Wrapper Generator — API helper functions.
// Follows the same pattern as the existing services/api.js in this project.

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach auth token automatically (matches existing interceptor pattern)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/**
 * Analyze an uploaded file for unsafe patterns.
 * @param {File} file  — JS File object from <input type="file">
 * @returns {Promise<WrapperResponse>}
 */
export const analyzeFileForWrappers = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/api/wrapper/analyze/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

/**
 * Analyze pasted code for unsafe patterns.
 * @param {string}      content   — raw source code
 * @param {string|null} language  — "Python" | "Java" | null (auto-detect)
 * @returns {Promise<WrapperResponse>}
 */
export const analyzeContentForWrappers = async (content, language = null) => {
  const res = await api.post('/api/wrapper/analyze/content', { content, language })
  return res.data
}

/**
 * Health check — confirms GROQ_API_KEY is configured server-side.
 */
export const wrapperHealthCheck = async () => {
  const res = await api.get('/api/wrapper/health')
  return res.data
}

export default api
