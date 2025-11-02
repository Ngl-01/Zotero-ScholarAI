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
  <div class="qa-container">
    <h2>🤖 智能问答</h2>
    <p class="page-desc">基于文献内容的 AI 驱动智能问答系统</p>

    <div class="input-section">
      <div class="input-card">
        <label class="input-label">💬 您的问题</label>
        <textarea 
          v-model="userInput" 
          placeholder="请输入您的问题，AI 将基于已选文献集回答..." 
          rows="5" 
          class="question-input"
        ></textarea>
        <div class="input-actions">
          <button @click="sendQuery" :disabled="loading" class="btn-send">
            <span v-if="loading">⏳ 思考中...</span>
            <span v-else>🚀 发送提问</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="statusMessage" class="status-message">
      <div class="spinner"></div>
      <span>{{ statusMessage }}</span>
    </div>

    <div v-if="augmentedPrompt" class="prompt-section">
      <div class="section-header">
        <h3>📝 增强提示词</h3>
        <button @click="copyToClipboard(augmentedPrompt)" class="btn-copy">
          📋 复制
        </button>
      </div>
      <div class="prompt-content">
        {{ augmentedPrompt }}
      </div>
    </div>

    <div v-if="llmResponse" class="response-section">
      <div class="section-header">
        <h3>💡 AI 回答</h3>
        <button @click="copyToClipboard(llmResponse)" class="btn-copy">
          📋 复制
        </button>
      </div>
      <div class="response-content" v-html="renderMarkdownWithLinks(llmResponse)" @click="handleLinkClickEvent"></div>
    </div>

    <div v-if="dialogVisible" class="modal-overlay" @click.self="dialogVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ dialogContent.title }}</h3>
          <button @click="dialogVisible = false" class="modal-close">✕</button>
        </div>
        <div class="modal-body">
          <p v-if="dialogContent.publication" class="modal-publication">
            📖 {{ dialogContent.publication }}
          </p>
          <div class="modal-text">
            {{ dialogContent.text }}
          </div>
        </div>
        <div class="modal-footer">
          <a :href="`zotero://select/library/items/${encodeURIComponent(dialogContent.key)}`" class="modal-btn">
            👁️ 在 Zotero 中查看
          </a>
          <a v-if="dialogContent.pdf_key" @click.prevent="openItem(dialogContent.pdf_key)" href="###" class="modal-btn">
            📄 打开 PDF
          </a>
          <button @click="dialogVisible = false" class="modal-btn modal-btn-close">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.qa-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-desc {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.input-section {
  margin-bottom: 30px;
}

.input-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.input-label {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.question-input {
  width: 100%;
  padding: 15px;
  font-size: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s ease;
  line-height: 1.6;
}

.question-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  outline: none;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.btn-send {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-send:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.status-message {
  background: #fff3cd;
  color: #856404;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: center;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.prompt-section,
.response-section {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h3 {
  color: #667eea;
  font-size: 20px;
  margin: 0;
}

.btn-copy {
  padding: 8px 16px;
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-copy:hover {
  background: #667eea;
  color: white;
}

.prompt-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  border-left: 4px solid #667eea;
}

.response-content {
  color: #333;
  font-size: 15px;
  line-height: 1.8;
}

.response-content :deep(h1),
.response-content :deep(h2),
.response-content :deep(h3) {
  color: #667eea;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
}

.response-content :deep(p) {
  margin-bottom: 1em;
}

.response-content :deep(code) {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #e83e8c;
}

.response-content :deep(pre) {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1em 0;
}

.response-content :deep(.link) {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(102, 126, 234, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.response-content :deep(.link:hover) {
  background: #667eea;
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 15px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 25px;
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.modal-header h3 {
  color: #667eea;
  font-size: 20px;
  margin: 0;
  flex: 1;
  padding-right: 20px;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e0e0e0;
  color: #666;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f8f9fa;
  border-color: #667eea;
  color: #667eea;
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
  flex: 1;
}

.modal-publication {
  color: #666;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 15px;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.modal-text {
  color: #666;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 2px solid #f0f0f0;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #fafafa;
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  border: none;
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.modal-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-1px);
}

.modal-btn-close {
  background: #e0e0e0;
  color: #666;
  border-color: #e0e0e0;
}

.modal-btn-close:hover {
  background: #d0d0d0;
  color: #333;
  border-color: #d0d0d0;
}
</style>
