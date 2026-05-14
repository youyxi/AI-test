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
    // 过滤掉错误消息
    const validMessages = messages.value.filter(m => !m.isError)
    if (validMessages.length === 0) {
      // 如果没有有效消息，但有当前对话，说明是对话被清空了，刷新历史记录
      if (currentConversation.value) {
        await loadConversations()
      }
      return null
    }
    
    try {
      let conv
      if (currentConversation.value) {
        conv = await api.updateConversation(currentConversation.value.id, {
          title: generateTitle(validMessages),
          messages: validMessages.map(m => ({
            role: m.role,
            content: m.content
          }))
        })
        currentConversation.value = conv
      } else {
        conv = await api.createConversation({
          title: generateTitle(validMessages),
          model: currentModel.value.id,
          provider: currentModel.value.provider,
          messages: validMessages.map(m => ({
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

  async function appendMessageToConversation(message) {
    if (!currentConversation.value) return null
    
    try {
      const conv = await api.appendMessage(currentConversation.value.id, message)
      
      // 如果是用户消息，更新对话标题为最新的提问
      if (message.role === 'user') {
        const updatedConv = await api.updateConversation(currentConversation.value.id, {
          title: generateTitle([...messages.value, message])
        })
        currentConversation.value = updatedConv
        await loadConversations()
      } else {
        currentConversation.value = conv
      }
      
      return conv
    } catch (error) {
      console.error('Failed to append message:', error)
      return null
    }
  }

  function generateTitle(messages) {
    // 获取最后一条用户消息作为标题
    const userMessages = messages.filter(m => m.role === 'user')
    const lastUserMessage = userMessages[userMessages.length - 1]
    if (lastUserMessage) {
      const content = lastUserMessage.content.trim()
      const firstLine = content.split('\n')[0]
      const title = firstLine.substring(0, 40)
      return title.length < firstLine.length ? title + '...' : title
    }
    return 'New Chat'
  }

  async function startNewConversation() {
    if (isLoading.value) return
    
    // 如果有当前对话且有消息，保存为历史记录
    if (messages.value.length > 0) {
      await saveCurrentConversation()
    }
    
    // 清空消息并开始新的对话空间
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

    // 保存用户消息到数据库
    if (currentConversation.value) {
      await appendMessageToConversation({
        role: 'user',
        content: content.trim()
      })
    } else {
      // 创建新对话
      await saveCurrentConversation()
    }

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
        const assistantMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: streamingContent.value
        }
        messages.value.push(assistantMessage)
        
        // 保存助手回复到数据库
        await appendMessageToConversation({
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
