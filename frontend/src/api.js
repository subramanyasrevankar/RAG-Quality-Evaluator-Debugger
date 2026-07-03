import axios from 'axios'

const BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Upload a document
export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  return response.data
}

// Query the document
export const queryDocument = async (question, topK = 3) => {
  const response = await api.post('/query', {
    question,
    top_k: topK   // ✅ Backend expects top_k
  })

  return response.data
}

// Get evaluation history
export const getHistory = async (limit = 10) => {
  const response = await api.get(`/history?limit=${limit}`) // ✅ Fixed template literal
  return response.data
}

// Get dashboard statistics
export const getStats = async () => {
  const response = await api.get('/stats')
  return response.data
}

// Clear cache
export const clearCache = async () => {
  const response = await api.delete('/cache/clear')
  return response.data
}

// Get cache statistics
export const getCacheStats = async () => {
  const response = await api.get('/cache/stats')
  return response.data
}

// Get available templates
export const getTemplates = async () => {
  const response = await api.get('/templates')
  return response.data
}

export default api