import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  // Dataset operations
  async uploadDataset(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getDatasets() {
    const response = await api.get('/upload/datasets')
    return response.data
  },

  async getDataset(id) {
    const response = await api.get(`/upload/datasets/${id}`)
    return response.data
  },

  async getDatasetPreview(id) {
    const response = await api.get(`/upload/datasets/${id}/preview`)
    return response.data
  },

  async deleteDataset(id) {
    const response = await api.delete(`/upload/datasets/${id}`)
    return response.data
  },

  // Model operations
  async trainModel(modelData) {
    const response = await api.post('/ml/train', modelData)
    return response.data
  },

  async getModels() {
    const response = await api.get('/ml/models')
    return response.data
  },

  async getModel(id) {
    const response = await api.get(`/ml/models/${id}`)
    return response.data
  },

  async getModelResults(id) {
    const response = await api.get(`/ml/models/${id}/results`)
    return response.data
  },

  async deleteModel(id) {
    const response = await api.delete(`/ml/models/${id}`)
    return response.data
  },

  async makePrediction(modelId, data) {
    const response = await api.post(`/ml/models/${modelId}/predict`, data)
    return response.data
  },

  // Report operations
  async downloadPdfReport(modelId) {
    const response = await api.get(`/reports/${modelId}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  async downloadCsvResults(modelId) {
    const response = await api.get(`/reports/${modelId}/csv`, {
      responseType: 'blob',
    })
    return response.data
  },

  async getModelCharts(modelId) {
    const response = await api.get(`/reports/${modelId}/charts`)
    return response.data
  },

  async getModelSummary(modelId) {
    const response = await api.get(`/reports/${modelId}/summary`)
    return response.data
  }
} 