<template>
  <div class="flex-1 overflow-y-auto">
    <!-- 顶部导航栏 -->
    <header class="h-14 border-b border-gray-100 bg-white flex items-center px-4">
      <button
        @click="goBack"
        class="p-2 hover:bg-gray-100 rounded-lg transition-colors mr-3"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-gray-800">设置</h1>
    </header>

    <div class="max-w-2xl mx-auto p-6">
      <!-- Profile Section -->
      <div class="bg-white rounded-xl border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">个人资料</h2>

        <!-- Avatar -->
        <div class="flex items-center gap-4 mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
            {{ avatarLetter }}
          </div>
          <div>
            <div class="font-medium text-gray-800">{{ authStore.user?.nickname || authStore.user?.username }}</div>
            <div class="text-sm text-gray-500">@{{ authStore.user?.username }}</div>
          </div>
        </div>

        <!-- Nickname -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">昵称</label>
          <input
            v-model="profileForm.nickname"
            type="text"
            placeholder="您的显示名称"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Email (read-only) -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
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
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors text-sm"
        >
          {{ savingProfile ? '保存中...' : '保存资料' }}
        </button>
      </div>

      <!-- Chat Settings -->
      <div class="bg-white rounded-xl border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">聊天设置</h2>

        <!-- Default Model -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">默认模型</label>
          <select
            v-model="settingsForm.default_model"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">自动（使用最近选择的）</option>
            <option v-for="m in chatStore.availableModels" :key="m.id" :value="m.id">
              {{ m.name }} ({{ m.providerName }})
            </option>
          </select>
        </div>

        <!-- Temperature -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            温度: {{ settingsForm.temperature }}
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
            <span>精确</span>
            <span>创意</span>
          </div>
        </div>

        <!-- Max Tokens -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">最大令牌数</label>
          <input
            v-model.number="settingsForm.max_tokens"
            type="number"
            placeholder="例如 2048"
            min="100"
            max="128000"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Send with Enter -->
        <div class="flex items-center justify-between mb-4">
          <div>
            <div class="text-sm font-medium text-gray-700">Enter 发送</div>
            <div class="text-xs text-gray-500">使用 Shift+Enter 换行</div>
          </div>
          <button
            @click="settingsForm.send_with_enter = !settingsForm.send_with_enter"
            class="relative w-11 h-6 rounded-full transition-colors"
            :class="settingsForm.send_with_enter ? 'bg-blue-500' : 'bg-gray-300'"
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
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors text-sm"
        >
          {{ savingSettings ? '保存中...' : '保存设置' }}
        </button>
      </div>

      <!-- Change Password -->
      <div class="bg-white rounded-xl border p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">修改密码</h2>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">当前密码</label>
          <input
            v-model="passwordForm.old_password"
            type="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">新密码</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="至少6位字符"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          @click="handleChangePassword"
          :disabled="changingPassword"
          class="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors text-sm"
        >
          {{ changingPassword ? '修改中...' : '修改密码' }}
        </button>
      </div>

      <!-- Danger Zone -->
      <div class="bg-white rounded-xl border border-red-200 p-6">
        <h2 class="text-lg font-semibold text-red-600 mb-2">账户</h2>
        <p class="text-sm text-gray-500 mb-4">在此设备上退出您的账户。</p>
        <button
          @click="handleLogout"
          class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
        >
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
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

function goBack() {
  router.push('/')
}

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
    alert('新密码长度至少6位')
    return
  }
  changingPassword.value = true
  try {
    await authStore.changePassword(passwordForm.old_password, passwordForm.new_password)
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    alert('密码修改成功')
  } catch (error) {
    alert(error.response?.data?.detail || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
