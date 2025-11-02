<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'

interface SearchItem {
  document: string
  key: string
  distance: number
  title: string
  publication: string
  pdf_key: string
}

const query = ref('')
const n_results = ref(40)
const results = ref<SearchItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedKeys = inject('selectedKeys') as Ref<string[]>

async function doSearch() {
  if (!query.value.trim()) {
    results.value = []
    return
  }

  loading.value = true
  error.value = null
  try {
    const res = await fetch(`/api/semantic_search?n_results=${n_results.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: [query.value], collections: selectedKeys.value }),
    })
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
    // semantic_search now returns items without title/publication/pdf_key
    const data = (await res.json()) as Array<{ document: string; key: string; distance: number }>
    // Show initial results immediately
    results.value = data.map(item => ({ ...item, title: '正在获取……', publication: '正在获取……', pdf_key: '' }))

    // For each item, fetch details asynchronously and merge into results
    for (const [i, item] of data.entries()) {
      fetch(`/api/item/${encodeURIComponent(item.key)}`)
        .then(async r => {
          if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
          const info = await r.json()
          // info = { title, pdf_key, publication }
          // Update the corresponding item in results
          results.value[i] = {
            ...results.value[i],
            title: info.title ?? '',
            publication: info.publication ?? '',
            pdf_key: info.pdf_key ?? '',
          }
        })
        .catch(() => {
          // If error, leave fields blank
        })
    }
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  } finally {
    loading.value = false
  }
}

const openItem = (key: string) => {
  fetch(`/api/open/${encodeURIComponent(key)}`, { method: 'GET' })
}

const exportItem = (key: string) => {
  fetch(`/api/export/${encodeURIComponent(key)}`, { method: 'GET' })
}

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
  <h2>语义搜索</h2>
  <p style="display: flex; gap: 0.5em;">
    <input v-model="query" @keypress.enter="doSearch" style="width:400px;" />
    <span>最多</span>
    <input type="number" v-model.number="n_results" min="1" max="200" style="width: 3em; text-align: right;" />
    <span>个结果</span>
    <button type="button" @click="doSearch" :disabled="loading">搜索</button>
    <button type="button" @click="exportAll">导出全部</button>
    <button type="button" @click="openExportPath">打开目录</button>
  </p>
  <p v-if="loading">搜索中…</p>
  <p v-else-if="error">错误：{{ error }}</p>
  <div v-else>
    <p v-if="results.length === 0">未找到结果</p>
    <div v-for="item in results" :key="item.key">
      <h3>{{ item.title || '无标题' }}</h3>
      <p>
        <span v-if="item.publication">{{ item.publication }}</span>
        <span style="margin-left: 0.5em;">距离: {{ item.distance.toFixed(3) }}</span>
      </p>
      <p style="font-size: 0.6em;">{{ item.document }}</p>
      <p style="display: flex; gap: 0.5em;">
        <a :href="`zotero://select/library/items/${encodeURIComponent(item.key)}`">查看</a>
        <a v-if="item.pdf_key" href="###" @click.prevent="openItem(item.pdf_key)">打开PDF</a>
        <a v-if="item.pdf_key" href="###" @click.prevent="exportItem(item.pdf_key)">导出PDF</a>
      </p>
    </div>
  </div>
</template>

<style></style>
