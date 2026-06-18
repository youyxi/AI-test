<template>
  <aside
    class="h-full bg-gray-50 text-gray-800 transition-all duration-300 flex flex-col shadow-sm relative"
    :class="collapsed ? 'w-16' : 'w-72'"
  >
    <!-- 用户信息头部 -->
    <div class="p-4 border-b border-gray-100 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-medium text-sm">
          AI
        </div>
        <div v-if="!collapsed">
          <div class="font-medium">AI Chat Hub</div>
        </div>
      </div>
      <!-- 右上角图标 -->
      <button
        v-if="!collapsed"
        class="w-6 h-6 border border-gray-300 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors"
      >
        <svg class="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
          <rect x="9" y="5" width="10" height="14" rx="1.5" stroke-linejoin="round" />
        </svg>
      </button>
    </div>

    <!-- 新对话按钮 -->
    <div class="p-3" v-if="!collapsed">
      <button
        @click="newChat"
        class="w-full py-3 px-4 bg-gray-100 hover:bg-gray-200 rounded-xl flex items-center gap-3 transition-colors group"
      >
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span class="font-medium text-gray-700">新对话</span>
        <span class="ml-auto text-xs text-gray-400 font-medium">Ctrl K</span>
      </button>
    </div>

    <!-- 功能菜单 -->
    <div class="px-3 space-y-1" v-if="!collapsed">
      <button class="w-full py-3 px-4 hover:bg-gray-100 rounded-xl flex items-center gap-3 transition-colors text-left">
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
        <span class="text-gray-700">AI 创作</span>
      </button>
      <button class="w-full py-3 px-4 hover:bg-gray-100 rounded-xl flex items-center gap-3 transition-colors text-left bg-gray-100">
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <span class="text-gray-700">云盘</span>
      </button>
      <button class="w-full py-3 px-4 hover:bg-gray-100 rounded-xl flex items-center gap-3 transition-colors text-left">
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
        <span class="text-gray-700">更多</span>
        <svg class="w-4 h-4 text-gray-400 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <!-- 历史对话分隔 -->
    <div class="px-4 py-3 text-xs text-gray-400 font-medium uppercase tracking-wider" v-if="!collapsed">
      历史对话
    </div>

    <!-- 对话列表 -->
    <div class="flex-1 overflow-y-auto px-2" v-if="!collapsed">
      <!-- 空状态 -->
      <div v-if="store.conversations.length === 0" class="px-4 py-8 text-center text-gray-400 text-sm">
        <div class="text-gray-300 text-4xl mb-2">💬</div>
        <div>暂无对话</div>
      </div>

      <!-- 对话列表 -->
      <div class="space-y-0.5">
        <div
          v-for="conv in store.conversations"
          :key="conv.id"
          @click="selectConversation(conv)"
          class="py-2.5 px-3 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors group flex items-start gap-3"
          :class="{ 'bg-gray-100': store.currentConversation?.id === conv.id }"
        >
          <!-- 消息气泡图标 -->
          <svg class="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          
          <!-- 对话标题 -->
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-700 truncate">{{ conv.title }}</div>
          </div>
          
          <!-- 删除按钮 -->
          <button
            @click.stop="showDeleteConfirm(conv.id, $event)"
            class="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-all shrink-0 text-gray-400 hover:text-red-500"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认框 -->
    <div
      v-if="confirmBox.visible"
      class="fixed z-50 bg-white rounded-xl shadow-xl border border-gray-200 p-4 w-64"
      :style="{ left: confirmBox.x + 'px', top: confirmBox.y + 'px' }"
    >
      <div class="text-sm text-gray-700 mb-4">确定要删除这个对话吗？</div>
      <div class="flex gap-3">
        <button
          @click="cancelDelete"
          class="flex-1 py-2 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm transition-colors"
        >
          取消
        </button>
        <button
          @click="confirmDelete"
          class="flex-1 py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm transition-colors"
        >
          删除
        </button>
      </div>
    </div>

    <!-- 底部设置区域 -->
    <div class="border-t border-gray-100 p-3" v-if="!collapsed">
      <div class="flex items-center gap-3 px-3 py-2">
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <div class="flex-1">
          <div class="text-sm font-medium text-gray-700">用户</div>
        </div>
        <button
          @click="$emit('toggle')"
          class="p-1.5 hover:bg-gray-100 rounded transition-colors text-gray-400"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'

defineProps({
  collapsed: Boolean
})

defineEmits(['toggle'])

const store = useChatStore()

const confirmBox = reactive({
  visible: false,
  conversationId: null,
  x: 0,
  y: 0
})

onMounted(() => {
  store.loadConversations()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

function handleClickOutside(event) {
  if (confirmBox.visible) {
    cancelDelete()
  }
}

function newChat() {
  store.clearMessages()
}

async function selectConversation(conv) {
  await store.loadConversationMessages(conv.id)
}

function showDeleteConfirm(id, event) {
  event.stopPropagation()
  const rect = event.target.getBoundingClientRect()
  confirmBox.conversationId = id
  confirmBox.x = rect.left - 140
  confirmBox.y = rect.top - 80
  confirmBox.visible = true
}

function cancelDelete() {
  confirmBox.visible = false
  confirmBox.conversationId = null
}

async function confirmDelete() {
  if (confirmBox.conversationId) {
    await store.deleteConversation(confirmBox.conversationId)
  }
  cancelDelete()
}
</script>
