# LiuAgent 安装指南

## 环境要求

- Python 3.8+
- Conda 或 Python venv
- Node.js 16+ (可选，用于前端开发)

## 1. 创建虚拟环境

### 使用 Conda (推荐)

```bash
# 创建虚拟环境
conda create -n liu_agent python=3.11 -y

# 激活环境
conda activate liu_agent
```

### 使用 venv

```bash
# 创建虚拟环境
python -m venv liu_agent

# 激活环境 (Linux/Mac)
source liu_agent/bin/activate

# 激活环境 (Windows)
liu_agent\Scripts\activate
```

## 2. 安装Python依赖

```bash
# 确保在虚拟环境中
cd /home/user/work_01/liuagent

# 安装依赖
pip install -r requirements.txt
```

## 3. 配置设置

```bash
# 复制配置文件
cp config/config.example.toml config/config.toml

# 编辑配置文件
nano config/config.toml
```

### 必要配置项

在 `config/config.toml` 中设置以下API密钥：

```toml
[llm]
provider = "openai"
api_key = "your-openai-api-key"  # 替换为您的OpenAI API密钥

# 可选：Claude API
[llm.anthropic]
api_key = "your-anthropic-key"   # 替换为您的Anthropic API密钥

# 可选：Google搜索API
[search.google]
api_key = "your-google-api-key"
search_engine_id = "your-search-engine-id"
```

## 4. 创建必要目录

```bash
mkdir -p data logs uploads
```

## 5. 测试安装

```bash
# 运行测试脚本
python test_app.py
```

## 6. 启动应用

```bash
# 启动后端服务
python main.py
```

访问 http://localhost:8000 查看应用

## 7. 前端开发 (可选)

如果需要修改前端：

```bash
cd frontend

# 安装Node.js依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## API密钥获取

### OpenAI API
1. 访问 https://platform.openai.com/api-keys
2. 创建新的API密钥
3. 复制密钥到配置文件

### Anthropic API (可选)
1. 访问 https://console.anthropic.com/
2. 创建API密钥
3. 复制密钥到配置文件

### Google Search API (可选)
1. 访问 https://console.developers.google.com/
2. 启用Custom Search API
3. 创建API密钥和搜索引擎ID

## 故障排除

### 常见问题

1. **模块未找到错误**
   ```bash
   # 确保在虚拟环境中
   which python
   pip list
   ```

2. **权限错误**
   ```bash
   # 给脚本执行权限
   chmod +x scripts/*.sh
   ```

3. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 或修改配置文件中的端口
   ```

4. **API密钥错误**
   - 检查配置文件中的API密钥格式
   - 确认API密钥有效且有余额

### 验证安装

运行以下命令验证各组件：

```bash
# 检查Python环境
python --version
pip list | grep -E "(fastapi|openai|anthropic)"

# 检查配置
python -c "from app.core import get_config; print('Config loaded successfully')"

# 检查API连接
curl http://localhost:8000/api/health
```

## 下一步

1. 配置API密钥
2. 上传PDF文档到知识库
3. 开始使用智能对话功能
4. 探索网络搜索功能

## 技术支持

如遇到问题，请检查：
1. 虚拟环境是否正确激活
2. 所有依赖是否安装完成
3. 配置文件是否正确设置
4. API密钥是否有效
