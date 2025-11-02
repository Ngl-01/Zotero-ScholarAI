# Zotero ScholarAI 智能文献查阅系统

<div align="center">

一个基于 AI 的智能文献管理与检索系统，结合 Zotero 文献库，提供语义搜索、全文搜索和智能问答功能。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![Vue](https://img.shields.io/badge/vue-3.5+-brightgreen.svg)

</div>

## ✨ 功能特性

- 📚 **Zotero 集成**：无缝对接 Zotero 文献库，自动读取文献集和 PDF 文件
- 🔍 **语义搜索**：基于向量嵌入的智能语义检索，理解查询意图
- 📝 **全文搜索**：支持关键词全文检索，快速定位相关文献
- 🤖 **智能问答**：利用大语言模型回答文献相关问题，自动引用来源
- 📊 **文献索引**：自动提取 PDF 内容并建立向量索引
- 🎯 **多集合支持**：可同时检索多个文献集合
- 💡 **查询增强**：自动扩展用户查询以提高检索准确度
- 📤 **PDF 管理**：支持 PDF 打开、导出等便捷操作

## 🏗️ 技术架构

### 后端技术栈

- **框架**：FastAPI
- **向量数据库**：ChromaDB
- **大语言模型**：
  - 嵌入模型：dengcao/Qwen3-Embedding-0.6B
  - 对话模型：deepseek-ai/DeepSeek-V3
- **PDF 处理**：PyMuPDF
- **其他**：OpenAI API、httpx、tokenizers

### 前端技术栈

- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **路由**：Vue Router
- **Markdown 渲染**：marked

## 📦 安装部署

### 前置要求

- **后端**：Python 3.13+
- **前端**：Node.js 20.19.0+ 或 22.12.0+
- **Zotero**：本地安装的 Zotero 文献管理软件
- **嵌入模型服务**：Ollama 或其他兼容 OpenAI API 的服务
- **LLM 服务**：SiliconFlow API 或其他兼容 OpenAI API 的服务

### 后端安装

1. **克隆项目**

```bash
git clone <repository-url>
cd "Zotero ScholarAI/backend"
```

2. **安装依赖**

推荐使用 `uv` 或 `pip`（强烈推荐使用uv）：

```bash
# 使用 uv
uv sync

# 或使用 pip
pip install -e .
```

3. **配置文件**

复制 `_config.toml` 为 `config.toml` 并修改配置：

```toml
zotero_path = "你的Zotero文献路径"
static_path = "../frontend/dist"

[embedding]
model = "你的嵌入模型"
tokenizer = "tokenizer名称"
base_url = "模型API地址"
api_key = "你的API密钥"

[chat]
model = "你的对话模型"
base_url = "模型API地址"
api_key = "你的API密钥"
```

4. **启动后端服务**

```bash
python main.py
```

后端将在 `http://localhost:8000` 启动。

### 前端安装

1. **进入前端目录**

```bash
cd ../frontend
```

2. **安装依赖**

```bash
pnpm install
```

3. **开发模式运行**

```bash
pnpm dev
```

4. **生产环境构建**

```bash
pnpm build
```

构建后的文件将输出到 `dist` 目录，后端会自动提供静态文件服务。

## 🚀 使用指南

### 1. 索引文献

首次使用需要先索引 Zotero 文献集：

1. 启动应用后，在左侧选择要索引的文献集
2. 点击"索引文献集"按钮
3. 等待索引完成（首次索引可能需要较长时间）

### 2. 语义搜索

1. 进入"语义搜索"页面
2. 选择要检索的文献集
3. 输入自然语言查询，如"机器学习在医疗诊断中的应用"
4. 查看检索结果并浏览相关文献

### 3. 全文搜索

1. 进入"全文搜索"页面
2. 选择要检索的文献集
3. 输入关键词（支持多个关键词）
4. 查看包含关键词的文献片段

### 4. 智能问答

1. 进入"智能问答"页面
2. 选择相关的文献集作为知识库
3. 提出问题，如"什么是深度学习？"
4. AI 将基于文献内容回答问题，并提供引用链接

### 5. PDF 操作

- **查看详情**：点击文献标题查看详细信息
- **打开 PDF**：点击"打开"按钮使用系统默认阅读器打开
- **导出 PDF**：点击"导出"按钮将 PDF 复制到导出目录

## 📁 项目结构

```
Zotero ScholarAI/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI 主程序
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库操作（ChromaDB）
│   ├── llm.py              # 大语言模型交互
│   ├── zotero.py           # Zotero 接口
│   ├── config.toml         # 配置文件
│   ├── pyproject.toml      # Python 项目配置
│   └── data/               # 数据目录
│       ├── chroma/         # 向量数据库存储
│       └── export/         # PDF 导出目录
│
└── frontend/               # 前端应用
    ├── src/
    │   ├── App.vue         # 主应用组件
    │   ├── main.ts         # 入口文件
    │   ├── router/         # 路由配置
    │   └── views/          # 页面组件
    │       ├── Home.vue            # 首页
    │       ├── SemanticSearch.vue  # 语义搜索
    │       ├── FullTextSearch.vue  # 全文搜索
    │       └── LLMQA.vue           # 智能问答
    ├── package.json        # 前端依赖配置
    └── vite.config.ts      # Vite 配置
```

## 🔧 API 文档

启动后端服务后，访问以下地址查看完整 API 文档：

- Scalar API 文档：`http://localhost:8000/scalar`
- OpenAPI Schema：`http://localhost:8000/openapi.json`

### 主要 API 端点

- `GET /api/collections` - 获取所有文献集
- `POST /api/index_collections` - 索引指定文献集
- `POST /api/semantic_search` - 语义搜索
- `POST /api/fulltext_search` - 全文搜索
- `POST /api/get_full_prompt` - 生成智能问答提示词
- `GET /api/item/{key}` - 获取文献详情
- `GET /api/open/{key}` - 打开 PDF
- `GET /api/export/{key}` - 导出 PDF

## 🎨 界面预览

系统提供三个主要功能模块：

1. **语义搜索**：基于向量相似度的智能检索
2. **全文搜索**：基于关键词的精确匹配
3. **智能问答**：基于文献内容的 AI 问答

## ⚙️ 配置说明

### Zotero 路径配置

`zotero_path` 应指向 Zotero 的数据目录，通常位于：
- Windows: `C:\Users\<用户名>\Zotero`
- macOS: `/Users/<用户名>/Zotero`
- Linux: `~/Zotero`

### 模型配置

系统支持任何兼容 OpenAI API 的服务：

- **嵌入模型**：用于文本向量化，推荐使用专门的 embedding 模型
- **对话模型**：用于智能问答，推荐使用大型语言模型

### 提示词配置

可以在 `config.toml` 的 `[prompt]` 部分自定义：

- `enhance`：查询增强提示词
- `ask`：问答提示词

## 🐛 常见问题

### 1. 找不到 Zotero 文献库

检查 `config.toml` 中的 `zotero_path` 是否正确指向 Zotero 数据目录。

### 2. 索引速度慢

- 首次索引需要处理所有 PDF，耗时较长是正常现象
- 后续索引会跳过未修改的文件，速度会快很多
- 可以考虑只索引常用的文献集

### 3. 嵌入模型连接失败

确保：
- Ollama 服务正在运行
- `base_url` 配置正确
- 模型已下载到本地

### 4. 问答结果不准确

尝试：
- 优化查询问题的表述
- 扩大检索的文献集范围
- 调整 `config.toml` 中的提示词

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- [Zotero](https://www.zotero.org/) - 开源文献管理工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [DeepSeek](https://www.deepseek.com/) - 大语言模型服务
- [Qwen](https://github.com/QwenLM) - 嵌入模型

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](../../issues)
- 发起 [Discussion](../../discussions)

---

<div align="center">
Made with ❤️ for researchers and scholars
</div>
