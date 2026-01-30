import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Analysis endpoints
export const analyzeFile = async (formData, projectId = null) => {
  const response = await api.post('/api/analyze/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    params: projectId ? { project_id: projectId } : {},
  })
  return response.data
}

export const analyzeContent = async (content, projectId = null) => {
  const response = await api.post('/api/analyze/content', {
    content,
    project_id: projectId,
  })
  return response.data
}

export const analyzeFilePath = async (filePath) => {
  const response = await api.get(`/api/analyze/${encodeURIComponent(filePath)}`)
  return response.data
}

export const getSupportedExtensions = async () => {
  const response = await api.get('/api/supported-extensions')
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/api/health')
  return response.data
}

// Authentication endpoints
export const registerUser = async (userData) => {
  const response = await api.post('/api/auth/register', userData)
  return response.data
}

export const loginUser = async (credentials) => {
  const response = await api.post('/api/auth/login', credentials)
  if (response.data.access_token) {
    localStorage.setItem('auth_token', response.data.access_token)
  }
  return response.data
}

export const logoutUser = () => {
  localStorage.removeItem('auth_token')
}

export const getCurrentUser = () => {
  const token = localStorage.getItem('auth_token')
  if (!token) return null
  // Decode JWT token (simple implementation)
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload
  } catch {
    return null
  }
}

// Project endpoints
export const createProject = async (projectData) => {
  const response = await api.post('/api/projects', projectData)
  return response.data
}

export const getProjects = async () => {
  const response = await api.get('/api/projects')
  return response.data
}

export const getProject = async (projectId) => {
  const response = await api.get(`/api/projects/${projectId}`)
  return response.data
}

// Technical debt endpoint
export const getTechnicalDebtSummary = async (projectId = null) => {
  const response = await api.get('/api/analysis/technical-debt', {
    params: projectId ? { project_id: projectId } : {},
  })
  return response.data
}

export default api
