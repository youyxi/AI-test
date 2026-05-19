<template>
  <div class="relative" ref="selectorRef">
    <button 
      @click="isOpen = !isOpen"
      class="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
    >
      <span class="text-sm font-medium">{{ currentModel.name }}</span>
      <span class="text-xs text-gray-500">{{ currentModel.providerName }}</span>
      <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    
    <div 
      v-if="isOpen"
      class="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg border z-50 overflow-hidden"
    >
      <div class="max-h-96 overflow-y-auto">
        <div 
          v-for="provider in groupedModels" 
          :key="provider.id"
          class="border-b last:border-b-0"
        >
          <div class="px-4 py-2 bg-gray-50 text-xs font-medium text-gray-500 uppercase">
            {{ provider.name }}
            <span v-if="!provider.configured" class="ml-2 text-amber-500">(未配置)</span>
          </div>
          <div class="p-2">
            <button
              v-for="model in provider.models"
              :key="model.id"
              @click="selectModel(model)"
              class="w-full text-left px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors"
              :class="{ 'bg-primary-50 text-primary-700': isSelected(model) }"
            >
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">{{ model.name }}</span>
                <span v-if="model.supports_vision" class="text-xs bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded">
                  视觉
                </span>
              </div>
              <div class="text-xs text-gray-500 mt-0.5">
                最大 {{ formatTokens(model.max_tokens) }} tokens
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'

const store = useChatStore()
const isOpen = ref(false)
const selectorRef = ref(null)

const currentModel = computed(() => store.currentModel)

const groupedModels = computed(() => {
  return store.providers.map(provider => ({
    id: provider.id,
    name: provider.name,
    configured: provider.configured,
    models: provider.models
  }))
})

onMounted(() => {
  store.loadProviders()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

function handleClickOutside(event) {
  if (selectorRef.value && !selectorRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

function selectModel(model) {
  store.setModel(model)
  isOpen.value = false
}

function isSelected(model) {
  return store.currentModel.id === model.id && store.currentModel.provider === model.provider
}

function formatTokens(tokens) {
  if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`
  if (tokens >= 1000) return `${(tokens / 1000).toFixed(0)}K`
  return tokens
}
</script>
