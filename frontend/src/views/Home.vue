<script setup lang="ts">
import { ref, inject } from 'vue'
import type { Ref } from 'vue'

const indexingProgress = ref('未开始')
const selectedKeys = inject('selectedKeys') as Ref<string[]>

async function startIndexing() {
  if (!selectedKeys || selectedKeys.value.length === 0) {
    alert('请先选择文献集合！')
    return
  }
  console.log(selectedKeys.value);


  const response = await fetch('/api/index_collections', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(selectedKeys.value),
  })

  if (!response.ok) {
    indexingProgress.value = `请求失败：${response.statusText}`
    return
  }

  const reader = response.body?.getReader()
  if (!reader) {
    indexingProgress.value = '无法读取服务器响应'
    return
  }

  const decoder = new TextDecoder()
  let done = false
  indexingProgress.value = '索引中...'

  while (!done) {
    const { value, done: readerDone } = await reader.read()
    done = readerDone
    if (value) {
      const chunk = decoder.decode(value, { stream: true })
      indexingProgress.value = chunk // 更新进度
    }
  }

  indexingProgress.value = '索引完成'
}
</script>

<template>
  <div>
    <h2>主页</h2>
    <p>欢迎来到 Zotero 助手！</p>
    <p>这里可以借助大模型来检索 Zotero 中的文献。</p>
    <p>请使用上方的导航栏进行操作。</p>
    <p>如果你是开发者，可以点击 <a href="/scalar">这个链接</a> 查看后端 API 文档</p>
    <h3>使用说明</h3>
    <ol>
      <li>在左侧勾选文献集合</li>
      <li>点击这个 <button @click="startIndexing">索引</button> 按钮</li>
      <li>现在的索引进度是：{{ indexingProgress }}</li>
    </ol>
  </div>
</template>
