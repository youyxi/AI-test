import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([])
  const conversations = ref([])
  const currentConversation = ref(null)
  const isLoading = ref(false)
  const streamingContent = ref('')
  const isStopped = ref(false)

  // Current model
  const currentModel = ref({
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    providerName: 'OpenAI'
  })

  const availableModels = ref([])
  const providers = ref([])

  // Computed
  const hasMessages = computed(() => messages.value.length > 0)

  // Methods
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
      console.error('Failed to load providers:', error)
    }
  }

  async function loadConversations() {
    try {
      const data = await api.getConversations()
      conversations.value = data
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }

  async function loadConversationMessages(conversationId) {
    try {
      const conv = await api.getConversation(conversationId)
      currentConversation.value = conv
      messages.value = conv.messages || []
      return conv
    } catch (error) {
      console.error('Failed to load conversation messages:', error)
      return null
    }
  }

  async function saveCurrentConversation() {
    if (messages.value.length === 0) return null
    
    try {
      let conv
      if (currentConversation.value) {
        conv = await api.createConversation({
          id: currentConversation.value.id,
          title: generateTitle(messages.value),
          model: currentModel.value.id,
          provider: currentModel.value.provider,
          messages: messages.value.map(m => ({
            role: m.role,
            content: m.content
          }))
        })
        currentConversation.value = conv
      } else {
        conv = await api.createConversation({
          title: generateTitle(messages.value),
          model: currentModel.value.id,
          provider: currentModel.value.provider,
          messages: messages.value.map(m => ({
            role: m.role,
            content: m.content
          }))
        })
        currentConversation.value = conv
      }
      
      await loadConversations()
      return conv
    } catch (error) {
      console.error('Failed to save conversation:', error)
      return null
    }
  }

  function generateTitle(messages) {
    const firstUserMessage = messages.find(m => m.role === 'user')
    if (firstUserMessage) {
      const title = firstUserMessage.content.substring(0, 30)
      return title.length < firstUserMessage.content.length ? title + '...' : title
    }
    return 'New Chat'
  }

  async function startNewConversation() {
    if (isLoading.value) return
    
    if (messages.value.length > 0) {
      await saveCurrentConversation()
    }
    
    messages.value = []
    currentConversation.value = null
    streamingContent.value = ''
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
      await api.streamChat({
        messages: messages.value.map(m => ({
          role: m.role,
          content: m.content
        })),
        model: currentModel.value.id,
        provider: currentModel.value.provider,
        stream: true
      }, (chunk) => {
        streamingContent.value += chunk
      })

      if (streamingContent.value) {
        messages.value.push({
          id: Date.now() + 1,
          role: 'assistant',
          content: streamingContent.value
        })
      }

      streamingContent.value = ''
    } catch (error) {
      if (error.name === 'AbortError') {
        if (streamingContent.value) {
          messages.value.push({
            id: Date.now() + 1,
            role: 'assistant',
            content: streamingContent.value + '\n\n*[Stopped]*'
          })
        }
        streamingContent.value = ''
      } else {
        console.error('Failed to send message:', error)
        messages.value.push({
          id: Date.now() + 1,
          role: 'assistant',
          content: `Error: ${error.message}`,
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

  return {
    // State
    messages,
    conversations,
    currentConversation,
    isLoading,
    streamingContent,
    isStopped,
    currentModel,
    availableModels,
    providers,

    // Computed
    hasMessages,

    // Methods
    loadProviders,
    loadConversations,
    loadConversationMessages,
    saveCurrentConversation,
    startNewConversation,
    sendMessage,
    stopGeneration,
    clearMessages,
    setModel,
    deleteConversation
  }
})
