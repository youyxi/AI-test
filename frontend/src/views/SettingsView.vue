<template>
  <div class="flex-1 overflow-y-auto p-6">
    <div class="max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-gray-800 mb-6">Settings</h1>

      <!-- Profile Section -->
      <div class="bg-white rounded-xl border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Profile</h2>

        <!-- Avatar -->
        <div class="flex items-center gap-4 mb-6">
          <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-2xl font-bold">
            {{ avatarLetter }}
          </div>
          <div>
            <div class="font-medium text-gray-800">{{ authStore.user?.nickname || authStore.user?.username }}</div>
            <div class="text-sm text-gray-500">@{{ authStore.user?.username }}</div>
          </div>
        </div>

        <!-- Nickname -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
          <input
            v-model="profileForm.nickname"
            type="text"
            placeholder="Your display name"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Email (read-only) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            :value="authStore.user?.email"
            type="email"
            disabled
            class="w-full px-4 py-2 border border-gray-200 bg-gray-50 rounded-lg text-gray-500"
          />
        </div>

        <button
          @click="saveProfile"
          :disabled="savingProfile"
          class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-colors text-sm"
        >
          {{ savingProfile ? 'Saving...' : 'Save Profile' }}
        </button>
      </div>

      <!-- Chat Settings -->
      <div class="bg-white rounded-xl border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Chat Settings</h2>

        <!-- Default Model -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Default Model</label>
          <select
            v-model="settingsForm.default_model"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Auto (use last selected)</option>
            <option v-for="m in chatStore.availableModels" :key="m.id" :value="m.id">
              {{ m.name }} ({{ m.providerName }})
            </option>
          </select>
        </div>

        <!-- Temperature -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Temperature: {{ settingsForm.temperature }}
          </label>
          <input
            v-model.number="settingsForm.temperature"
            type="range"
            min="0"
            max="2"
            step="0.1"
            class="w-full"
          />
          <div class="flex justify-between text-xs text-gray-400 mt-1">
            <span>Precise</span>
            <span>Creative</span>
          </div>
        </div>

        <!-- Max Tokens -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
          <input
            v-model.number="settingsForm.max_tokens"
            type="number"
            placeholder="e.g. 2048"
            min="100"
            max="128000"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Send with Enter -->
        <div class="flex items-center justify-between mb-4">
          <div>
            <div class="text-sm font-medium text-gray-700">Send with Enter</div>
            <div class="text-xs text-gray-500">Use Shift+Enter for new line</div>
          </div>
          <button
            @click="settingsForm.send_with_enter = !settingsForm.send_with_enter"
            class="relative w-11 h-6 rounded-full transition-colors"
            :class="settingsForm.send_with_enter ? 'bg-primary-500' : 'bg-gray-300'"
          >
            <span
              class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
              :class="settingsForm.send_with_enter ? 'translate-x-5' : ''"
            ></span>
          </button>
        </div>

        <button
          @click="saveSettings"
          :disabled="savingSettings"
          class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-colors text-sm"
        >
          {{ savingSettings ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>

      <!-- Change Password -->
      <div class="bg-white rounded-xl border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Change Password</h2>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
          <input
            v-model="passwordForm.old_password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">New Password</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="min 6 characters"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <button
          @click="handleChangePassword"
          :disabled="changingPassword"
          class="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors text-sm"
        >
          {{ changingPassword ? 'Changing...' : 'Change Password' }}
        </button>
      </div>

      <!-- Danger Zone -->
      <div class="bg-white rounded-xl border border-red-200 p-6">
        <h2 class="text-lg font-semibold text-red-600 mb-2">Account</h2>
        <p class="text-sm text-gray-500 mb-4">Sign out of your account on this device.</p>
        <button
          @click="handleLogout"
          class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
        >
          Sign Out
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const savingProfile = ref(false)
const savingSettings = ref(false)
const changingPassword = ref(false)

const avatarLetter = computed(() => {
  const name = authStore.user?.nickname || authStore.user?.username || ''
  return name.charAt(0).toUpperCase()
})

const profileForm = reactive({
  nickname: ''
})

const settingsForm = reactive({
  default_model: '',
  temperature: 0.7,
  max_tokens: null,
  send_with_enter: true
})

const passwordForm = reactive({
  old_password: '',
  new_password: ''
})

onMounted(() => {
  if (authStore.user) {
    profileForm.nickname = authStore.user.nickname || ''
    const s = authStore.user.settings || {}
    settingsForm.default_model = s.default_model || ''
    settingsForm.temperature = s.temperature ?? 0.7
    settingsForm.max_tokens = s.max_tokens || null
    settingsForm.send_with_enter = s.send_with_enter ?? true
  }
  chatStore.loadProviders()
})

async function saveProfile() {
  savingProfile.value = true
  try {
    await authStore.updateProfile({ nickname: profileForm.nickname })
  } finally {
    savingProfile.value = false
  }
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await authStore.updateSettings({
      default_model: settingsForm.default_model || undefined,
      temperature: settingsForm.temperature,
      max_tokens: settingsForm.max_tokens || undefined,
      send_with_enter: settingsForm.send_with_enter
    })
  } finally {
    savingSettings.value = false
  }
}

async function handleChangePassword() {
  if (!passwordForm.old_password || !passwordForm.new_password) return
  if (passwordForm.new_password.length < 6) {
    alert('New password must be at least 6 characters')
    return
  }
  changingPassword.value = true
  try {
    await authStore.changePassword(passwordForm.old_password, passwordForm.new_password)
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    alert('Password changed successfully')
  } catch (error) {
    alert(error.response?.data?.detail || 'Failed to change password')
  } finally {
    changingPassword.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
