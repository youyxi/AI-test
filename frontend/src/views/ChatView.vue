<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- 消息列表 -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4"
    >
      <!-- 欢迎消息 -->
      <div v-if="!store.hasMessages" class="h-full flex items-center justify-center">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-primary-100 rounded-2xl flex items-center justify-center">
            <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-800 mb-2">AI Chat Hub</h2>
          <p class="text-gray-500 mb-6">Select an AI model to start chatting</p>
          
          <!-- 快速选择 -->
          <div class="grid grid-cols-2 gap-3 max-w-md mx-auto">
            <button 
              v-for="model in quickModels" 
              :key="model.id"
              @click="selectModel(model)"
              class="p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50 transition-all text-left"
            >
              <div class="font-medium text-gray-800">{{ model.name }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ model.providerName }}</div>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 消息列表 -->
      <template v-else>
        <ChatMessage 
          v-for="msg in store.messages" 
          :key="msg.id"
          :message="msg"
        />
        
        <!-- Streaming Output -->
        <div
          v-if="store.isLoading && store.streamingContent"
          class="message p-3 rounded-2xl bg-white border border-gray-200"
          style="width: fit-content; max-width: 85%;"
        >
          <div class="markdown-body prose prose-sm max-w-none" v-html="renderedStreaming"></div>
        </div>

        <!-- Loading Indicator -->
        <div v-if="store.isLoading && !store.streamingContent" class="flex items-center gap-2 text-gray-500">
          <div class="typing-indicator flex gap-1">
            <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
          </div>
          <span class="text-sm">Thinking...</span>
        </div>
      </template>
    </div>
    
    <!-- 输入区域 -->
    <div class="p-4 border-t bg-white">
      <div class="max-w-3xl mx-auto">
        <!-- 停止按钮 -->
        <div v-if="store.isLoading" class="flex justify-center mb-3">
          <button
            @click="stopGeneration"
            class="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-full hover:bg-gray-700 transition-colors text-sm"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="1.5" />
            </svg>
            Stop
          </button>
        </div>

        <div class="relative">
          <textarea
            ref="inputRef"
            v-model="inputText"
            @keydown="handleKeydown"
            placeholder="Type a message... (Shift+Enter for new line)"
            rows="1"
            class="w-full px-4 py-3 pr-12 bg-gray-100 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
            :disabled="store.isLoading"
          ></textarea>
          <!-- 发送按钮 / 停止按钮 -->
          <button
            v-if="!store.isLoading"
            @click="sendMessage"
            :disabled="!inputText.trim()"
            class="absolute right-2 bottom-2 p-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
          <button
            v-else
            @click="stopGeneration"
            class="absolute right-2 bottom-2 p-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="1.5" />
            </svg>
          </button>
        </div>
        <div class="text-xs text-gray-400 mt-2 text-center">
          Model: {{ store.currentModel.name }} · {{ store.currentModel.providerName }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { marked } from 'marked'
import { useChatStore } from '../stores/chat'
import ChatMessage from '../components/ChatMessage.vue'

const store = useChatStore()

const inputText = ref('')
const inputRef = ref(null)
const messagesContainer = ref(null)

// 快速选择模型
const quickModels = computed(() => {
  return store.availableModels.slice(0, 4)
})

// 渲染流式内容
const renderedStreaming = computed(() => {
  return marked.parse(store.streamingContent || '')
})

// 流式输出时自动滚动到底部
watch(() => store.streamingContent, async () => {
  await nextTick()
  scrollToBottom()
})

// 发送消息
async function sendMessage() {
  if (!inputText.value.trim() || store.isLoading) return
  
  const content = inputText.value
  inputText.value = ''
  
  await store.sendMessage(content)
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
}

// 停止生成
function stopGeneration() {
  store.stopGeneration()
}

// 处理键盘事件
function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 选择模型
function selectModel(model) {
  store.setModel(model)
}

// 滚动到底部
function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  store.loadProviders()
})
</script>
