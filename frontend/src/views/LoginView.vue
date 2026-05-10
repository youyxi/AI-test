<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 mx-auto mb-4 bg-primary-500 rounded-2xl flex items-center justify-center shadow-lg">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-800">AI Chat Hub</h1>
        <p class="text-gray-500 mt-1">{{ isLogin ? 'Sign in to continue' : 'Create your account' }}</p>
      </div>

      <!-- Form Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <!-- Tab Switch -->
        <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            @click="isLogin = true"
            class="flex-1 py-2 text-sm font-medium rounded-md transition-all"
            :class="isLogin ? 'bg-white shadow text-gray-800' : 'text-gray-500 hover:text-gray-700'"
          >
            Sign In
          </button>
          <button
            @click="isLogin = false"
            class="flex-1 py-2 text-sm font-medium rounded-md transition-all"
            :class="!isLogin ? 'bg-white shadow text-gray-800' : 'text-gray-500 hover:text-gray-700'"
          >
            Sign Up
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="errorMsg" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
          {{ errorMsg }}
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Username -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              v-model="form.username"
              type="text"
              placeholder="letters, numbers, underscores"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>

          <!-- Email (register only) -->
          <div v-if="!isLogin" class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>

          <!-- Password -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="min 6 characters"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
              minlength="6"
            />
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full py-2.5 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {{ authStore.loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account') }}
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-sm text-gray-400 mt-6">
        {{ isLogin ? "Don't have an account?" : 'Already have an account?' }}
        <button @click="isLogin = !isLogin" class="text-primary-500 hover:text-primary-600 font-medium">
          {{ isLogin ? 'Sign Up' : 'Sign In' }}
        </button>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const errorMsg = ref('')

const form = reactive({
  username: '',
  email: '',
  password: ''
})

async function handleSubmit() {
  errorMsg.value = ''

  try {
    if (isLogin.value) {
      await authStore.login(form.username, form.password)
    } else {
      if (!form.email) {
        errorMsg.value = 'Please enter your email'
        return
      }
      await authStore.register(form.username, form.email, form.password)
    }
    router.push('/')
  } catch (error) {
    const detail = error.response?.data?.detail
    errorMsg.value = detail || (isLogin.value ? 'Login failed' : 'Registration failed')
  }
}
</script>
