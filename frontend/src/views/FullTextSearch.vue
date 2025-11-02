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
  <h2>全文搜索</h2>
  <p style="display: flex; gap: 0.5em; align-items: center;">
    <input v-model="query" @keypress.enter="doSearch" style="width:400px;" />
    <label>
      <input type="checkbox" v-model="ignoreCase" id="ignore-case" />
      <span>忽略大小写</span>
    </label>
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
        <strong v-if="item.publication">{{ item.publication }}</strong>
      </p>
      <div>
        <p v-for="(line, i) in item.preview" :key="i" v-html="line"></p>
      </div>
      <p style="display: flex; gap: 0.5em;">
        <a :href="`zotero://select/library/items/${encodeURIComponent(item.key)}`">查看</a>
        <a v-if="item.pdf_key" href="###" @click.prevent="openItem(item.pdf_key)">打开PDF</a>
        <a v-if="item.pdf_key" href="###" @click.prevent="exportItem(item.pdf_key)">导出PDF</a>
      </p>
    </div>
  </div>
</template>
