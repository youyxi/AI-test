import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - attach token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ========== Auth API ==========
export async function register(data) {
  const response = await api.post('/auth/register', data)
  return response.data
}

export async function login(data) {
  const response = await api.post('/auth/login', data)
  return response.data
}

export async function getMe() {
  const response = await api.get('/auth/me')
  return response.data
}

export async function updateProfile(data) {
  const response = await api.put('/auth/profile', data)
  return response.data
}

export async function updateSettings(data) {
  const response = await api.put('/auth/settings', data)
  return response.data
}

export async function changePassword(oldPassword, newPassword) {
  const response = await api.put('/auth/password', null, {
    params: { old_password: oldPassword, new_password: newPassword }
  })
  return response.data
}

// ========== Chat API ==========
export async function getProviders() {
  const response = await api.get('/chat/providers')
  return response.data
}

export async function getModels() {
  const response = await api.get('/chat/models')
  return response.data
}

export async function chat(data) {
  const response = await api.post('/chat/completions', data)
  return response.data
}

// AbortController for stream
let currentAbortController = null

export async function streamChat(data, onChunk) {
  if (currentAbortController) {
    currentAbortController.abort()
  }

  currentAbortController = new AbortController()
  const signal = currentAbortController.signal

  const token = localStorage.getItem('token')
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    body: JSON.stringify(data),
    signal
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.content) {
              onChunk(data.content)
            }
          } catch (e) {
            // ignore
          }
        }
      }
    }
  } finally {
    currentAbortController = null
  }
}

export function stopStreaming() {
  if (currentAbortController) {
    currentAbortController.abort()
    currentAbortController = null
  }
}

// ========== Conversation API ==========
export async function getConversations() {
  const response = await api.get('/conversations')
  return response.data
}

export async function getConversation(id) {
  const response = await api.get(`/conversations/${id}`)
  return response.data
}

export async function createConversation(data) {
  const response = await api.post('/conversations', data)
  return response.data
}

export async function updateConversation(id, data) {
  const response = await api.put(`/conversations/${id}`, data)
  return response.data
}

export async function appendMessage(conversationId, message) {
  const response = await api.post(`/conversations/${conversationId}/messages`, message)
  return response.data
}

export async function deleteConversation(id) {
  const response = await api.delete(`/conversations/${id}`)
  return response.data
}
