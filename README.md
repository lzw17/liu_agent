# LiuAgent - AI Competition Agent

An intelligent AI agent built for the competition with comprehensive knowledge base, chat, and web search capabilities.

## 🎯 项目特色

1. **📚 PDF知识库**: 导入PDF文档，自动生成可搜索的向量知识库
2. **💬 智能对话**: 基于知识库内容的上下文感知问答
3. **🔍 网络搜索**: 实时网络搜索，获取最新信息
4. **🤖 多模型支持**: 支持OpenAI、Claude、Ollama等多种LLM API
5. **🌐 公开API**: 完整的RESTful API接口
6. **🎨 现代界面**: Vue.js前端，集成武昌工学院校徽

## 🏗️ 技术架构

- **后端**: FastAPI + 异步处理
- **前端**: Vue.js 3 + Element Plus UI
- **知识库**: ChromaDB向量数据库 + SentenceTransformer嵌入
- **LLM集成**: 灵活的适配器模式支持多种模型
- **搜索引擎**: DuckDuckGo、Google、Bing多引擎支持

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建conda虚拟环境 (推荐)
conda create -n liu_agent python=3.11 -y
conda activate liu_agent

# 或使用venv
python -m venv liu_agent
source liu_agent/bin/activate  # Linux/Mac
```

### 2. 安装依赖

```bash
cd /home/user/work_01/liuagent
pip install -r requirements.txt
```

### 3. 配置设置

```bash
# 复制配置文件
cp config/config.example.toml config/config.toml

# 编辑配置文件，添加API密钥
nano config/config.toml
```

**重要**: 需要设置以下API密钥：
- OpenAI API密钥 (必需)
- Anthropic API密钥 (可选)
- Google搜索API密钥 (可选)

### 4. 启动应用

```bash
# 创建必要目录
mkdir -p data logs uploads

# 启动服务
python main.py
```

```bash
nohup ./cloudflared tunnel --url http://localhost:8000 > cloudflared.log 2>&1 &
```

访问 http://localhost:8000 查看应用

## 📖 详细文档

- [安装指南](SETUP_GUIDE.md) - 详细的环境配置和安装步骤
- [部署指南](DEPLOYMENT.md) - 生产环境部署说明
- [API文档](http://localhost:8000/docs) - 启动后访问Swagger文档

## 🔌 API接口

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/chat` | POST | 智能对话 |
| `/api/upload-pdf` | POST | 上传PDF文档 |
| `/api/search` | POST | 网络搜索 |
| `/api/knowledge-base` | GET | 查看知识库 |
| `/api/health` | GET | 健康检查 |

## 🛠️ 开发测试

```bash
# 运行测试
python test_app.py

# 使用Docker
docker-compose up -d

# 查看日志
tail -f logs/liuagent.log
```

## 🎓 竞赛说明

本项目专为 [iCAN竞赛](http://contest.g-ican.com/competition/details?id=64) 开发，集成了：
- 武昌工学院品牌元素
- 完整的AI助手功能
- 可扩展的架构设计
- 生产级部署方案
