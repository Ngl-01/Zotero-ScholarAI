<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
import { ref, onMounted, provide } from 'vue'

interface Collection {
  key: string
  name: string
  numItems: number
}

const collections = ref<Collection[]>([])
const selectedKeys = ref<string[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

async function loadCollections() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/collections')
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    const data = (await res.json()) as Collection[]
    collections.value = data
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  } finally {
    loading.value = false
  }
}

provide('selectedKeys', selectedKeys)

onMounted(() => {
  loadCollections()
})

function toggleAllCollections(event: Event) {
  const target = event.target as HTMLInputElement;
  selectedKeys.value = target.checked ? collections.value.map(c => c.key) : [];
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3>📚 文献集合</h3>
    </div>
    
    <div class="sidebar-content">
      <label class="select-all">
        <input type="checkbox" :checked="selectedKeys.length === collections.length" @change="toggleAllCollections" />
        <span>全选</span>
      </label>

      <div v-if="loading" class="loading">⏳ 加载中…</div>
      <div v-else-if="error" class="error">❌ 加载失败：{{ error }}</div>
      <div v-else class="collections-list">
        <label v-for="col in collections" :key="col.key" class="collection-item" :title="col.name">
          <input type="checkbox" :value="col.key" v-model="selectedKeys" />
          <span class="collection-name">{{ col.name }}</span>
          <span class="collection-count">{{ col.numItems }}</span>
        </label>
      </div>
      
      <div class="selection-info">
        已选: <strong>{{ selectedKeys.length }}</strong> / {{ collections.length }}
      </div>
    </div>
  </aside>

  <section class="main-section">
    <header class="top-header">
      <div class="brand">
        <span class="logo">🎓</span>
        <span class="title">Zotero ScholarAI</span>
      </div>
      <nav class="nav-tabs">
        <RouterLink to="/" class="nav-link">🏠 主页</RouterLink>
        <RouterLink to="/semantic" class="nav-link">🔍 语义搜索</RouterLink>
        <RouterLink to="/fulltext" class="nav-link">📝 全文搜索</RouterLink>
        <RouterLink to="/llm" class="nav-link">🤖 智能问答</RouterLink>
      </nav>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </section>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.sidebar-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.select-all:hover {
  background: #e9ecef;
}

.collections-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.collection-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.collection-item:hover {
  background: #f8f9fa;
  border-color: #667eea;
  transform: translateX(5px);
}

.collection-item input[type="checkbox"] {
  cursor: pointer;
  width: 18px;
  height: 18px;
  accent-color: #667eea;
}

.collection-name {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.collection-count {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.selection-info {
  margin-top: 15px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.selection-info strong {
  color: #667eea;
  font-size: 16px;
}

.loading, .error {
  padding: 20px;
  text-align: center;
  border-radius: 8px;
  margin: 10px 0;
}

.loading {
  background: #fff3cd;
  color: #856404;
}

.error {
  background: #f8d7da;
  color: #721c24;
}

/* 主内容区样式 */
.main-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 70px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-size: 32px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-tabs {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  color: #666;
  font-weight: 500;
  transition: all 0.3s ease;
  background: white;
  border: 2px solid transparent;
}

.nav-link:hover {
  background: #f8f9fa;
  color: #667eea;
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background: rgba(255, 255, 255, 0.9);
  margin: 20px;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* 通用样式 */
h2, h3, h4 {
  margin: 0.6em 0 0.4em 0;
  color: #333;
}

h2 {
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 20px;
}

p {
  margin: 0.4em 0;
  line-height: 1.6;
}

input[type="text"],
input[type="number"],
textarea {
  padding: 10px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: inherit;
}

input[type="text"]:focus,
input[type="number"]:focus,
textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

button:active {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

a {
  color: #667eea;
  text-decoration: none;
  transition: all 0.3s ease;
}

a:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #764ba2;
}
</style>
