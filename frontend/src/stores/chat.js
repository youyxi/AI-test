import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api/chat'

const defaultProviders = [
  {
    id: 'openai',
    name: 'OpenAI',
    configured: false,
    models: [
      {
        id: 'gpt-4',
        name: 'GPT-4',
        provider: 'openai',
        providerName: 'OpenAI',
        supports_vision: true,
        max_tokens: 128000
      },
      {
        id: 'gpt-3.5-turbo',
        name: 'GPT-3.5 Turbo',
        provider: 'openai',
        providerName: 'OpenAI',
        supports_vision: false,
        max_tokens: 16385
      }
    ]
  },
  {
    id: 'claude',
    name: 'Claude',
    configured: false,
    models: [
      {
        id: 'claude-3-opus',
        name: 'Claude 3 Opus',
        provider: 'claude',
        providerName: 'Claude',
        supports_vision: true,
        max_tokens: 200000
      },
      {
        id: 'claude-3-sonnet',
        name: 'Claude 3 Sonnet',
        provider: 'claude',
        providerName: 'Claude',
        supports_vision: true,
        max_tokens: 200000
      }
    ]
  },
  {
    id: 'gemini',
    name: 'Gemini',
    configured: false,
    models: [
      {
        id: 'gemini-pro',
        name: 'Gemini Pro',
        provider: 'gemini',
        providerName: 'Gemini',
        supports_vision: true,
        max_tokens: 32768
      }
    ]
  },
  {
    id: 'qwen',
    name: '通义千问',
    configured: false,
    models: [
      {
        id: 'qwen-turbo',
        name: 'Qwen Turbo',
        provider: 'qwen',
        providerName: '通义千问',
        supports_vision: false,
        max_tokens: 8192
      },
      {
        id: 'qwen-plus',
        name: 'Qwen Plus',
        provider: 'qwen',
        providerName: '通义千问',
        supports_vision: false,
        max_tokens: 32768
      }
    ]
  }
]

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const conversations = ref([])
  const currentConversation = ref(null)
  const isLoading = ref(false)
  const streamingContent = ref('')
  const isStopped = ref(false)

  const currentModel = ref({
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    providerName: 'OpenAI'
  })

  const availableModels = ref([])
  const providers = ref([])

  const hasMessages = computed(() => messages.value.length > 0)

  async function loadProviders() {
    try {
      const data = await api.getProviders()
      providers.value = data

      const models = []
      data.forEach(provider => {
        provider.models.forEach(model => {
          models.push({
            ...model,
            providerName: provider.name,
            configured: provider.configured
          })
        })
      })
      availableModels.value = models

      const configuredModel = models.find(m => m.configured)
      if (configuredModel) {
        currentModel.value = configuredModel
      }
    } catch (error) {
      console.error('Failed to load providers, using defaults:', error)
      providers.value = defaultProviders
      
      const models = []
      defaultProviders.forEach(provider => {
        provider.models.forEach(model => {
          models.push({
            ...model,
            providerName: provider.name,
            configured: false
          })
        })
      })
      availableModels.value = models
    }
  }

  async function loadConversations() {
    try {
      const data = await api.getConversations()
      conversations.value = data
    } catch (error) {
      console.error('Failed to load conversations:', error)
      conversations.value = []
    }
  }

  async function loadConversationMessages(conversationId) {
    try {
      const conv = await api.getConversation(conversationId)
      currentConversation.value = conv
      messages.value = conv.messages || []
      
      // 如果对话有模型信息，更新当前模型
      if (conv.model && conv.provider) {
        const model = availableModels.value.find(
          m => m.id === conv.model && m.provider === conv.provider
        )
        if (model) {
          currentModel.value = model
        }
      }
      
      return conv
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
      return null
    }
  }

  async function sendMessage(content) {
    if (!content.trim() || isLoading.value) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: content.trim()
    }
    messages.value.push(userMessage)

    isLoading.value = true
    streamingContent.value = ''
    isStopped.value = false

    try {
      const response = await api.streamChat({
        messages: messages.value.map(m => ({
          role: m.role,
          content: m.content
        })),
        model: currentModel.value.id,
        provider: currentModel.value.provider,
        stream: true,
        conversation_id: currentConversation.value?.id || null
      }, (chunk) => {
        streamingContent.value += chunk
      })

      // 处理成功响应
      if (streamingContent.value) {
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: streamingContent.value
        }
        messages.value.push(assistantMessage)
      }

      streamingContent.value = ''
      
      // 刷新对话列表
      await loadConversations()
      
      // 如果是新对话，刷新当前对话以获取ID
      if (!currentConversation.value?.id) {
        const latestConversations = await api.getConversations()
        if (latestConversations.length > 0) {
          currentConversation.value = latestConversations[0]
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        if (streamingContent.value) {
          messages.value.push({
            id: Date.now() + 1,
            role: 'assistant',
            content: streamingContent.value + '\n\n*[已停止]*'
          })
        }
        streamingContent.value = ''
      } else {
        console.error('Failed to send message:', error)
        messages.value.push({
          id: Date.now() + 1,
          role: 'assistant',
          content: `错误: ${error.message}`,
          isError: true
        })
      }
    } finally {
      isLoading.value = false
      isStopped.value = false
    }
  }

  function stopGeneration() {
    isStopped.value = true
    api.stopStreaming()
  }

  function clearMessages() {
    messages.value = []
    currentConversation.value = null
  }

  function setModel(model) {
    currentModel.value = model
  }

  async function deleteConversation(conversationId) {
    try {
      await api.deleteConversation(conversationId)
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      if (currentConversation.value?.id === conversationId) {
        clearMessages()
      }
      return true
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      return false
    }
  }

  async function updateConversationTitle(conversationId, newTitle) {
    try {
      const updated = await api.updateConversation(conversationId, { title: newTitle })
      const index = conversations.value.findIndex(c => c.id === conversationId)
      if (index !== -1) {
        conversations.value[index] = { ...conversations.value[index], ...updated }
      }
      if (currentConversation.value?.id === conversationId) {
        currentConversation.value = { ...currentConversation.value, ...updated }
      }
      return true
    } catch (error) {
      console.error('Failed to update conversation title:', error)
      return false
    }
  }

  return {
    messages,
    conversations,
    currentConversation,
    isLoading,
    streamingContent,
    isStopped,
    currentModel,
    availableModels,
    providers,

    hasMessages,

    loadProviders,
    loadConversations,
    loadConversationMessages,
    sendMessage,
    stopGeneration,
    clearMessages,
    setModel,
    deleteConversation,
    updateConversationTitle
  }
})
