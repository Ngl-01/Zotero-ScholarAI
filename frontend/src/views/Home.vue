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
  <div class="home-container">
    <div class="hero-section">
      <h2>🎓 欢迎使用 Zotero ScholarAI</h2>
      <p class="subtitle">智能文献检索与问答系统</p>
      <p class="description">借助 AI 大模型的能力，帮您高效管理和检索 Zotero 文献库</p>
    </div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <h3>语义搜索</h3>
        <p>基于向量嵌入的智能检索，理解查询意图</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📝</div>
        <h3>全文搜索</h3>
        <p>支持关键词精确匹配，快速定位文献</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>智能问答</h3>
        <p>AI 驱动的文献问答，自动引用来源</p>
      </div>
    </div>

    <div class="guide-section">
      <h3>📋 快速开始</h3>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>选择文献集</h4>
            <p>在左侧勾选需要索引的文献集合</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>开始索引</h4>
            <button @click="startIndexing" class="index-button">
              📚 开始索引文献
            </button>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>索引进度</h4>
            <div class="progress-info" :class="{ 'in-progress': indexingProgress !== '未开始' && indexingProgress !== '索引完成' }">
              {{ indexingProgress }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="info-section">
      <div class="info-card">
        <p>💡 <strong>提示：</strong>首次索引可能需要较长时间，后续只会处理新增或修改的文献</p>
      </div>
      <div class="info-card developer">
        <p>👨‍💻 开发者文档：<a href="/scalar" target="_blank">查看 API 文档</a></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 15px;
  margin-bottom: 40px;
}

.hero-section h2 {
  font-size: 36px;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 20px;
  color: #666;
  font-weight: 500;
  margin-bottom: 10px;
}

.description {
  font-size: 16px;
  color: #888;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.feature-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
  border-color: #667eea;
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #667eea;
  margin-bottom: 10px;
}

.feature-card p {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.guide-section {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.guide-section h3 {
  color: #667eea;
  margin-bottom: 25px;
  font-size: 24px;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.step:hover {
  background: #e9ecef;
}

.step-number {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h4 {
  color: #333;
  margin-bottom: 8px;
  font-size: 18px;
}

.step-content p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.index-button {
  margin-top: 10px;
  font-size: 16px;
  padding: 12px 30px;
}

.progress-info {
  margin-top: 10px;
  padding: 12px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  color: #666;
  font-weight: 500;
}

.progress-info.in-progress {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  color: #667eea;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-card {
  background: #fff3cd;
  border: 2px solid #ffeaa7;
  padding: 15px 20px;
  border-radius: 10px;
  color: #856404;
}

.info-card.developer {
  background: #d1ecf1;
  border-color: #bee5eb;
  color: #0c5460;
}

.info-card p {
  margin: 0;
}

.info-card a {
  color: #0c5460;
  font-weight: 600;
}

.info-card a:hover {
  color: #667eea;
}
</style>
