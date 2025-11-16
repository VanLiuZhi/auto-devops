# Auto DevOps - 故障诊断AI助手

一个基于FastAPI和LangChain的自动化运维故障诊断系统。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方式1：直接启动
python main.py

# 方式2：使用启动脚本
./start.sh

# 方式3：激活虚拟环境后启动
source .venv/bin/activate
python main.py
```

### 3. 访问服务

- **API文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/api/health
- **聊天接口**: http://localhost:8002/api/chat
- **流式聊天**: http://localhost:8002/api/chat/stream

## 📚 API使用

### 健康检查
```bash
curl http://localhost:8002/api/health
```

### 同步聊天
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}'
```

### 流式聊天
```bash
curl -X POST http://localhost:8002/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}'
```

## 🏗️ 项目结构

```
auto-devops/
├── main.py                 # 启动入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖管理
├── start.sh              # 启动脚本
├── test_api.py           # API测试脚本
├── README.md             # 项目说明
├── .env.example          # 环境变量示例
└── src/                  # 源代码包
    ├── __init__.py
    └── demo/             # Demo模块
        ├── __init__.py
        ├── web_service.py     # 控制器层
        └── diagnosis_core.py  # 业务逻辑层
```

## 🔧 配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

配置项说明：
- `HOST`: 服务监听地址 (默认: 0.0.0.0)
- `PORT`: 服务端口 (默认: 8002)
- `DEBUG`: 调试模式 (默认: true)
- `RELOAD`: 热重载 (默认: true)

## 🧪 测试

运行API测试脚本：

```bash
python test_api.py
```

## 📖 功能特性

- **AI故障诊断**: 基于LangChain的智能诊断系统
- **流式响应**: 支持Server-Sent Events实时反馈
- **自动文档**: 完整的OpenAPI文档
- **分层架构**: 清晰的控制器和业务逻辑分离
- **热重载**: 开发环境自动重启

## 🛠️ 开发

### 添加新的API接口

1. 在 `src/demo/web_service.py` 中添加路由
2. 在 `src/demo/diagnosis_core.py` 中实现业务逻辑
3. 运行 `python main.py` 启动开发服务器

### 调试模式

启用详细日志：

```bash
export DIAGNOSIS_VERBOSE=true
python main.py
```

## 📄 许可证

MIT License