<template>
  <aside
    class="h-full bg-slate-800 text-white transition-all duration-300 flex flex-col"
    :class="collapsed ? 'w-16' : 'w-64'"
  >
    <!-- Header -->
    <div class="h-14 flex items-center justify-between px-4 border-b border-slate-700">
      <span v-if="!collapsed" class="font-semibold">History</span>
      <button
        @click="$emit('toggle')"
        class="p-1.5 hover:bg-slate-700 rounded transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>
    </div>

    <!-- New Chat Button -->
    <div class="p-3" v-if="!collapsed">
      <button
        @click="handleNewChat"
        :disabled="store.isLoading"
        class="w-full py-2.5 px-4 bg-primary-500 hover:bg-primary-600 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Chat
      </button>
    </div>

    <!-- Conversation List -->
    <div class="flex-1 overflow-y-auto" v-if="!collapsed">
      <!-- Empty State -->
      <div v-if="store.conversations.length === 0" class="px-3 py-8 text-center text-slate-400 text-sm">
        <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        No conversations yet
      </div>

      <!-- List -->
      <div class="px-3 space-y-1">
        <div
          v-for="conv in store.conversations"
          :key="conv.id"
          @click="selectConversation(conv)"
          class="p-3 hover:bg-slate-700 rounded-lg cursor-pointer transition-colors group"
          :class="{ 'bg-slate-700': store.currentConversation?.id === conv.id }"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="text-sm truncate">{{ conv.title }}</div>
              <div class="text-xs text-slate-400 mt-1 flex items-center gap-1">
                <span class="inline-block px-1.5 py-0.5 bg-slate-600 rounded text-[10px]">{{ conv.provider }}</span>
                <span>{{ formatTime(conv.updated_at) }}</span>
              </div>
            </div>
            <button
              @click.stop="deleteConv(conv.id)"
              class="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600 rounded transition-all shrink-0"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Settings -->
    <div class="p-3 border-t border-slate-700" v-if="!collapsed">
      <router-link
        to="/settings"
        class="w-full py-2 px-4 hover:bg-slate-700 rounded-lg flex items-center gap-2 text-sm text-slate-300 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Settings
      </router-link>
    </div>
  </aside>
</template>

<script setup>
import { onMounted } from 'vue'
import { useChatStore } from '../stores/chat'

defineProps({
  collapsed: Boolean
})

defineEmits(['toggle'])

const store = useChatStore()

onMounted(() => {
  store.loadConversations()
})

function newChat() {
  store.clearMessages()
}

async function handleNewChat() {
  await store.startNewConversation()
}

async function selectConversation(conv) {
  if (store.isLoading) return
  
  if (store.messages.length > 0 && store.currentConversation?.id !== conv.id) {
    await store.saveCurrentConversation()
  }
  
  await store.loadConversationMessages(conv.id)
}

async function deleteConv(id) {
  if (confirm('Delete this conversation?')) {
    await store.deleteConversation(id)
  }
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`
  return date.toLocaleDateString()
}
</script>
