<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'
import { marked } from 'marked'

const userInput = ref('')
const llmResponse = ref('')
const augmentedPrompt = ref('')
const loading = ref(false)
const statusMessage = ref('')
const dialogVisible = ref(false)
const dialogContent = ref({ title: '', publication: '', key: '', pdf_key: '', text: '' })
const selectedKeys = inject('selectedKeys') as Ref<string[]>

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    alert('内容已复制到剪贴板')
  } catch (err) {
    alert('复制失败')
  }
}

async function sendQuery() {
  if (!userInput.value.trim()) return

  loading.value = true
  llmResponse.value = ''
  augmentedPrompt.value = ''
  statusMessage.value = '正在获取增强的 Prompt...'

  try {
    // Step 1: Fetch augmented prompt
    const promptRes = await fetch(`/api/get_full_prompt?query=${encodeURIComponent(userInput.value)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedKeys.value),
    })
    if (!promptRes.ok) statusMessage.value = `Error fetching prompt: ${promptRes.status} ${promptRes.statusText}`

    const promptData = await promptRes.json()
    augmentedPrompt.value = promptData.prompt

    // Step 2: Generate response
    statusMessage.value = '正在生成回答...'
    const res = await fetch('/api/completion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([{ role: 'user', content: augmentedPrompt.value }]),
    })

    if (!res.ok) statusMessage.value = `Error generating response: ${res.status} ${res.statusText}`

    const reader = res.body?.getReader()
    if (!reader) {
      statusMessage.value = 'Error: No response body'
      return
    }

    const decoder = new TextDecoder()
    let done = false

    while (!done) {
      const { value, done: readerDone } = await reader.read()
      done = readerDone
      const text = decoder.decode(value, { stream: true })
      llmResponse.value += text
    }
  } catch (err: any) {
    llmResponse.value = `Error: ${err.message}`
  } finally {
    loading.value = false
    statusMessage.value = ''
  }
}

async function handleLinkClick(key: string) {
  try {
    const res = await fetch(`/api/get_document?key=${encodeURIComponent(key)}`)
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)

    const data = await res.json()
    dialogContent.value = {
      title: data.title || '',
      publication: data.publication || '',
      key: data.key || '',
      pdf_key: data.pdf_key || '',
      text: data.text || ''
    }
    dialogVisible.value = true
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err)
    alert(`Error fetching document: ${errorMessage}`)
  }
}

function renderMarkdownWithLinks(content: string) {
  // Replace [@key] with clickable spans
  const linkRegex = /\[@([A-Z0-9]{8}_\d+)]/g
  return marked(
    content.replace(linkRegex, (match, key) => {
      return `<span class='link' data-key='${key}'>${match}</span>`
    })
  )
}

function handleLinkClickEvent(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (target.classList.contains('link')) {
    const key = target.getAttribute('data-key')
    if (key) {
      handleLinkClick(key)
    }
  }
}

function openItem(key: string) {
  fetch(`/api/open/${encodeURIComponent(key)}`, { method: 'GET' })
}
</script>

<template>
  <h2>LLM问答</h2>
  <p>
    <textarea v-model="userInput" placeholder="输入您的问题..." rows="4" style="width:400px;"></textarea>
  </p>
  <p><button @click="sendQuery" :disabled="loading">发送</button></p>

  <p v-if="statusMessage">{{ statusMessage }}</p>

  <div v-if="augmentedPrompt">
    <p>{{ augmentedPrompt }}</p>
    <p><button @click="copyToClipboard(augmentedPrompt)">复制增强的 Prompt</button></p>
  </div>

  <div v-if="llmResponse" v-html="renderMarkdownWithLinks(llmResponse)" @click="handleLinkClickEvent"></div>
  <p><button @click="copyToClipboard(llmResponse)">复制回答</button></p>

  <div v-if="dialogVisible">
    <h3>{{ dialogContent.title }}</h3>
    <p>{{ dialogContent.publication }}</p>
    <p style="font-size: 0.6em;">{{ dialogContent.text }}</p>
    <p style="display: flex; gap: 0.5em;">
      <a :href="`zotero://select/library/items/${encodeURIComponent(dialogContent.key)}`" title="在Zotero中查看">查看</a>
      <a v-if="dialogContent.pdf_key" @click.prevent="openItem(dialogContent.pdf_key)" href="###">打开PDF</a>
      <a @click="dialogVisible = false" href="###">关闭</a>
    </p>
  </div>
</template>

<style>
.link {
  color: blue;
  text-decoration: underline;
  cursor: pointer;
}
</style>
