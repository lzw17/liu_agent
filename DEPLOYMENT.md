# LiuAgent 部署指南

## 快速开始

### 1. 环境准备

```bash
# 创建conda虚拟环境
conda create -n liu_agent python=3.11 -y
conda activate liu_agent

# 或使用venv
python -m venv liu_agent
source liu_agent/bin/activate  # Linux/Mac
# liu_agent\Scripts\activate  # Windows
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

# 编辑配置文件，添加您的API密钥
nano config/config.toml
```

**重要配置项：**
- `llm.api_key`: OpenAI API密钥
- `llm.anthropic.api_key`: Claude API密钥（可选）
- `search.google.api_key`: Google搜索API密钥（可选）

### 4. 启动应用

```bash
# 直接运行
python main.py

# 或使用脚本
./scripts/run.sh
```

访问 http://localhost:8000 查看应用

## Docker 部署

### 1. 使用 Docker Compose（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 使用 Docker

```bash
# 构建镜像
docker build -t liuagent .

# 运行容器
docker run -d \
  --name liuagent \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  liuagent
```

## 公网部署

### 1. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 使用 PM2 进程管理

```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start main.py --name liuagent --interpreter python

# 查看状态
pm2 status

# 查看日志
pm2 logs liuagent
```

### 3. 使用 Systemd 服务

创建 `/etc/systemd/system/liuagent.service`:

```ini
[Unit]
Description=LiuAgent AI Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/liuagent
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable liuagent
sudo systemctl start liuagent
```

## API 文档

启动应用后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能

### 1. 智能对话
- **端点**: `POST /api/chat`
- **功能**: 基于知识库和网络搜索的智能问答

### 2. PDF知识库
- **上传**: `POST /api/upload-pdf`
- **查询**: `GET /api/knowledge-base`
- **搜索**: `POST /api/knowledge-base/search`

### 3. 网络搜索
- **端点**: `POST /api/search`
- **支持**: DuckDuckGo、Google、Bing

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 杀死进程
   kill -9 <PID>
   ```

2. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   # 清除缓存
   pip cache purge
   ```

3. **API密钥错误**
   - 检查 `config/config.toml` 中的API密钥
   - 确保密钥有效且有足够额度

4. **前端无法访问**
   - 检查CORS设置
   - 确认防火墙规则

### 日志查看

```bash
# 查看应用日志
tail -f logs/liuagent.log

# 查看Docker日志
docker-compose logs -f liuagent
```

## 性能优化

### 1. 数据库优化
- 使用PostgreSQL替代SQLite（生产环境）
- 配置连接池

### 2. 缓存优化
- 启用Redis缓存
- 配置向量数据库索引

### 3. 负载均衡
- 使用多个应用实例
- 配置Nginx负载均衡

## 安全建议

1. **API密钥安全**
   - 使用环境变量存储密钥
   - 定期轮换密钥

2. **网络安全**
   - 使用HTTPS
   - 配置防火墙规则

3. **访问控制**
   - 实现用户认证
   - 设置API限流

## 监控和维护

### 1. 健康检查
```bash
curl http://localhost:8000/api/health
```

### 2. 性能监控
- 使用Prometheus + Grafana
- 监控API响应时间
- 监控资源使用情况

### 3. 备份策略
- 定期备份知识库数据
- 备份配置文件
- 备份用户上传的文档
