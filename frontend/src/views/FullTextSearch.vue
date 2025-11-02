<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'

const selectedKeys = inject('selectedKeys') as Ref<string[]>
const query = ref('')
const ignoreCase = ref(true);

const results = ref<Array<{ title: string; publication: string; key: string; pdf_key: string; preview: string }>>([]);
const loading = ref(false);
const error = ref<string | null>(null);

async function doSearch() {
  if (!query.value.trim()) {
    results.value = [];
    return;
  }

  loading.value = true;
  error.value = null;
  try {
    const res = await fetch('/api/fulltext_search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query.value.split('&&'),
        collections: selectedKeys.value,
        ignore_case: ignoreCase.value,
      }),
    });

    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

    const data = (await res.json()) as Array<{
      title: string;
      publication: string;
      key: string;
      pdf_key: string;
      preview: string;
    }>;

    results.value = data;
  } catch (err: any) {
    error.value = err?.message ?? String(err);
  } finally {
    loading.value = false;
  }
}

const openItem = (key: string) => {
  fetch(`/api/open/${encodeURIComponent(key)}`, { method: 'GET' });
};

const exportItem = (key: string) => {
  fetch(`/api/export/${encodeURIComponent(key)}`, { method: 'GET' });
};

const exportAll = () => {
  const keys: Record<string, boolean> = {}
  for (const item of results.value) {
    keys[item.key] = true
  }
  for (const key of Object.keys(keys)) {
    exportItem(key)
  }
}

const openExportPath = () => {
  fetch('/api/open_export_path', { method: 'GET' })
}
</script>

<template>
  <div class="search-container">
    <h2>📝 全文搜索</h2>
    <p class="page-desc">基于关键词的精确全文匹配检索</p>

    <div class="search-bar">
      <input 
        v-model="query" 
        @keypress.enter="doSearch" 
        class="search-input" 
        placeholder="输入关键词，使用 && 分隔多个关键词..." 
      />
      <div class="search-options">
        <label class="checkbox-label">
          <input type="checkbox" v-model="ignoreCase" id="ignore-case" />
          <span>忽略大小写</span>
        </label>
        <button type="button" @click="doSearch" :disabled="loading" class="btn-primary">
          🔍 搜索
        </button>
        <button type="button" @click="exportAll" class="btn-secondary">
          📥 导出全部
        </button>
        <button type="button" @click="openExportPath" class="btn-secondary">
          📂 打开目录
        </button>
      </div>
    </div>

    <div v-if="loading" class="status-message loading">
      <div class="spinner"></div>
      <span>搜索中，请稍候...</span>
    </div>
    <div v-else-if="error" class="status-message error">
      ❌ 错误：{{ error }}
    </div>
    <div v-else class="results-section">
      <div v-if="results.length === 0" class="no-results">
        <div class="no-results-icon">📝</div>
        <p>未找到相关结果，请尝试其他关键词</p>
      </div>
      <div v-else class="results-list">
        <div class="results-header">
          <span>找到 <strong>{{ results.length }}</strong> 条匹配结果</span>
        </div>
        <div v-for="(item, index) in results" :key="item.key" class="result-card">
          <div class="result-index">{{ index + 1 }}</div>
          <div class="result-content">
            <h3 class="result-title">{{ item.title || '无标题' }}</h3>
            <div class="result-meta">
              <span v-if="item.publication" class="publication">📖 {{ item.publication }}</span>
            </div>
            <div class="preview-section">
              <div v-for="(line, i) in item.preview" :key="i" v-html="line" class="preview-line"></div>
            </div>
            <div class="result-actions">
              <a :href="`zotero://select/library/items/${encodeURIComponent(item.key)}`" class="action-link">
                👁️ 在 Zotero 中查看
              </a>
              <a v-if="item.pdf_key" href="###" @click.prevent="openItem(item.pdf_key)" class="action-link">
                📄 打开 PDF
              </a>
              <a v-if="item.pdf_key" href="###" @click.prevent="exportItem(item.pdf_key)" class="action-link">
                💾 导出 PDF
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-desc {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.search-bar {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.search-input {
  width: 100%;
  padding: 15px 20px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.search-options {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.status-message {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  margin-bottom: 20px;
}

.status-message.loading {
  background: #fff3cd;
  color: #856404;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
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

.status-message.error {
  background: #f8d7da;
  color: #721c24;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.no-results-icon {
  font-size: 64px;
  margin-bottom: 15px;
  opacity: 0.5;
}

.no-results p {
  color: #666;
  font-size: 16px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.results-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 10px;
  color: #667eea;
  font-weight: 500;
}

.result-card {
  display: flex;
  gap: 20px;
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.result-card:hover {
  border-color: #667eea;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.result-index {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  flex-shrink: 0;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-title {
  color: #333;
  font-size: 20px;
  margin-bottom: 10px;
  font-weight: 600;
}

.result-meta {
  margin-bottom: 15px;
}

.publication {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.preview-section {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #667eea;
}

.preview-line {
  color: #666;
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 8px;
}

.preview-line:last-child {
  margin-bottom: 0;
}

.result-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-link {
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.action-link:hover {
  background: #667eea;
  color: white;
  transform: translateY(-1px);
  text-decoration: none;
}
</style>
