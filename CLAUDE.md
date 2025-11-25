# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 规范要求
回答，思考过程 都使用中文

需要操作python的时候，必须使用 当前目录下的 .venv 虚拟环境 来完成，禁止使用其它 python 环境

## 项目概览

这是一个基于FastAPI和LangChain的自动化运维故障诊断系统，提供Web界面和API服务。项目采用分层架构设计，支持流式响应和智能故障诊断。

### 核心架构

1. **Web层** (`src/demo/web_service.py`): FastAPI路由和HTTP处理
2. **业务逻辑层** (`src/demo/diagnosis_core.py`): 故障诊断核心逻辑，使用MockLLM模拟LangChain Agent
3. **基础组件层** (`src/base/agent.py`): 真实的LLM集成（GLM-4.6）和Agent执行器
4. **配置管理** (`config.py`): 环境变量和应用配置

### 关键技术栈
- **FastAPI**: Web框架，支持自动API文档
- **LangChain**: AI Agent框架，提供工具调用能力
- **Uvicorn**: ASGI服务器
- **Pydantic**: 数据验证和序列化

## 常用开发命令

### 环境设置
```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 启动服务
```bash
# 开发模式（支持热重载）
python main.py

# 或使用启动脚本
./start.sh
```

### 测试
```bash
# API测试
python test_api.py
```

### 服务访问地址
- 前端页面: http://localhost:8002/
- API文档: http://localhost:8002/docs
- 健康检查: http://localhost:8002/api/health

## 配置管理

项目支持环境变量配置，优先级：
1. 系统环境变量
2. `.env` 文件
3. 代码默认值

关键配置项：
- `HOST`: 服务监听地址（默认: 0.0.0.0）
- `PORT`: 服务端口（默认: 8002）
- `DEBUG`: 调试模式（默认: true）
- `RELOAD`: 热重载（默认: true）

## 代码结构说明

### 诊断系统架构
系统提供两种LLM实现：
1. **MockLLM** (`diagnosis_core.py`): 模拟响应，用于演示和离线运行
2. **GLMLLM** (`base/agent.py`): 真实的智谱GLM-4.6 API集成

### 核心组件
- **DiagnosisService**: 主要诊断服务，支持同步和流式响应
- **SimpleAgentExecutor**: Agent执行器，处理工具调用和对话流程
- **工具集成**: 预定义故障诊断工具（日志获取、知识库查询等）

### API设计
- `/api/chat`: 同步聊天接口
- `/api/chat/stream`: 流式聊天，支持Server-Sent Events
- `/api/health`: 健康检查

## 开发指南

### 添加新的诊断工具
1. 在相应文件中使用 `@tool` 装饰器定义工具函数
2. 在工具集合中注册新工具
3. 更新LLM提示词以包含新工具说明

### 修改诊断流程
诊断流程主要通过LLM提示词控制，位于：
- `DiagnosisService._get_prompt()` 方法
- `PROMPT_TEMPLATE` 常量

### 调试模式
启用详细日志：
```bash
export DIAGNOSIS_VERBOSE=true
python main.py
```

## 注意事项

- 项目使用Python虚拟环境，必须通过 `.venv/bin/activate` 激活
- MockLLM和GLMLLM有不同的配置和使用场景
- 流式响应使用Server-Sent Events协议
- 支持CORS跨域访问，生产环境需限制具体域名