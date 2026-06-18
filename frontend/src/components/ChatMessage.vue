<template>
  <div
    class="message p-3 rounded-2xl max-w-[85%] sm:max-w-[80%] md:max-w-[75%] lg:max-w-[70%]"
    :class="[
      message.role === 'user'
        ? 'bg-primary-500 text-white ml-auto'
        : 'bg-white border border-gray-200',
      { 'border-red-200 bg-red-50': message.isError }
    ]"
    style="width: fit-content;"
  >
    <!-- User Message -->
    <div v-if="message.role === 'user'" class="whitespace-pre-wrap break-words">
      {{ message.content }}
    </div>

    <!-- Assistant Message -->
    <div v-else class="markdown-body prose prose-sm max-w-none">
      <div v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

marked.setOptions({
  breaks: true,
  gfm: true
})

const renderedContent = computed(() => {
  if (props.message.role === 'user') return ''
  return marked.parse(props.message.content || '')
})
</script>
