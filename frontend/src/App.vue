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
  <aside style="width: 240px;">
    <h3>Collections</h3>
    <label>
      <input type="checkbox" :checked="selectedKeys.length === collections.length" @change="toggleAllCollections" />
      <span>全选</span>
    </label>

    <p v-if="loading">加载中…</p>
    <p v-else-if="error">加载失败：{{ error }}</p>
    <ol v-else>
      <li v-for="col in collections" :key="col.key">
        <label :title="col.name">
          <input type="checkbox" :value="col.key" v-model="selectedKeys" />
          <span>{{ col.name }} ({{ col.numItems }})</span>
        </label>
      </li>
    </ol>
    <p>已选: {{ selectedKeys.length }}/{{ collections.length }}</p>

  </aside>

  <section style="flex: 1; display: flex; flex-direction: column;">
    <header>
      <nav style="border-bottom: 1px solid black;">
        <p style="display: flex; gap: 0.5em;">
          <RouterLink to="/">主页</RouterLink>
          <RouterLink to="/fulltext">全文搜索</RouterLink>
          <RouterLink to="/semantic">语义搜索</RouterLink>
          <RouterLink to="/llm">LLM问答</RouterLink>
        </p>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </section>
</template>

<style>
h2,
h3,
h4,
ol,
p {
  margin-block-start: 0.4em;
  margin-block-end: 0.4em;
}

#app {
  display: flex;
}

input {
  padding: 3px;
}
</style>
