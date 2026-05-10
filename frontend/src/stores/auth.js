import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api/chat'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // Init from localStorage
  function init() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken && savedUser) {
      token.value = savedToken
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        logout()
      }
    }
  }

  async function login(username, password) {
    loading.value = true
    try {
      const data = await api.login({ username, password })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    } finally {
      loading.value = false
    }
  }

  async function register(username, email, password) {
    loading.value = true
    try {
      const data = await api.register({ username, email, password })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      const data = await api.getMe()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch {
      logout()
    }
  }

  async function updateProfile(profileData) {
    const data = await api.updateProfile(profileData)
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
    return data
  }

  async function updateSettings(settingsData) {
    const data = await api.updateSettings(settingsData)
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
    return data
  }

  async function changePassword(oldPassword, newPassword) {
    await api.changePassword(oldPassword, newPassword)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    user, token, loading, isLoggedIn,
    init, login, register, fetchUser,
    updateProfile, updateSettings, changePassword, logout
  }
})
