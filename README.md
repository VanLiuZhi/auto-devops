# Auto DevOps - 故障诊断AI助手

一个基于FastAPI和标准化ReAct架构的智能化自动化运维故障诊断系统。

## 🚀 新架构特性

- **✅ 完整ReAct流程**: 标准化的思考-行动循环，真正的AI决策
- **🔄 动态场景配置**: 支持5种预定义场景，可灵活自定义
- **🔧 双模型支持**: Mock模型用于开发测试，真实模型用于生产
- **🏗️ 分层架构**: 模块化设计，高内聚低耦合
- **📋 完全兼容**: 保持所有原有API接口不变

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

- **前端页面**: http://localhost:8002/
- **API文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/api/health
- **聊天接口**: http://localhost:8002/api/chat
- **流式聊天**: http://localhost:8002/api/chat/stream

## 🎨 前端界面

启动服务后访问 http://localhost:8002/ 即可使用美观的前端界面，包含：

- **💬 智能对话**: 与AI助手实时交互
- **🌊 流式响应**: 实时查看AI分析过程
- **⚡ 快速操作**: 预设常用故障诊断场景
- **📊 系统状态**: 实时监控服务健康状态
- **📱 响应式设计**: 支持桌面和移动设备

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

## 🏗️ 新架构项目结构

```
auto-devops/
├── main.py                     # 启动入口
├── config.py                   # 配置文件
├── requirements.txt            # 依赖管理
├── test_new_agent.py          # 新架构测试脚本
├── README.md                  # 项目说明
├── .env.example               # 环境变量示例
├── doc/                       # 📚 文档目录
│   ├── ARCHITECTURE_REFACTOR.md  # 架构重构文档
│   ├── QUICK_START.md           # 快速开始指南
│   ├── API_GUIDE.md            # API使用指南
│   └── SCENARIO_GUIDE.md       # 场景配置指南
└── src/                       # 📦 源代码包
    ├── core/                   # 🧠 新架构核心模块
    │   ├── models/              # 模型层
    │   │   ├── base_llm.py     # LLM基类
    │   │   ├── mock_llm.py     # 增强Mock模型
    │   │   ├── glm_llm.py      # GLM真实模型
    │   │   └── model_factory.py # 模型工厂
    │   ├── tools/               # 工具层
    │   │   ├── diagnosis_tools.py # 诊断工具
    │   │   └── tool_manager.py   # 工具管理器
    │   ├── agents/              # Agent层
    │   │   ├── react_executor.py  # ReAct执行器
    │   │   └── diagnosis_agent.py # 诊断Agent
    │   ├── services/            # 服务层
    │   │   └── diagnosis_service.py # 诊断服务
    │   └── configs/             # 配置层
    │       ├── scenarios.py       # 场景配置
    │       └── agent_configs.py  # Agent配置
    └── demo/                     # 🎯 兼容层
        ├── diagnosis_core.py  # 适配器（使用新架构）
        ├── diagnosis_core_old.py # 原始实现（备份）
        └── web_service.py      # FastAPI路由
```

## 🔧 配置

项目使用 `.env` 文件管理配置，支持环境变量自动读取。

### 配置文件

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 8002 | 服务端口 |
| `DEBUG` | true | 调试模式 |
| `RELOAD` | true | 热重载（开发环境） |
| `API_PREFIX` | /api | API路径前缀 |
| `DOCS_URL` | /docs | API文档路径 |
| `DIAGNOSIS_VERBOSE` | false | 诊断服务详细日志 |

### 环境变量优先级

1. 系统环境变量
2. `.env` 文件中的变量
3. 代码中的默认值

### 配置加载

配置通过 `python-dotenv` 库自动加载，在 `config.py` 中统一管理：

```python
from dotenv import load_dotenv
load_dotenv()  # 自动加载.env文件
```

## 🧪 测试

运行API测试脚本：

```bash
python test_api.py
```

## 📖 功能特性

- **🤖 AI故障诊断**: 基于标准化ReAct流程的智能诊断系统
- **🌊 流式响应**: 支持Server-Sent Events实时反馈，展示完整诊断过程
- **🔄 动态场景**: 支持5种预定义故障场景和自定义场景配置
- **🔧 模型切换**: 支持Mock模型和真实模型（GLM-4.6）的无缝切换
- **📋 自动文档**: 完整的OpenAPI文档和交互式测试界面
- **🏗️ 分层架构**: 模块化设计，清晰的控制器和业务逻辑分离
- **🔄 热重载**: 开发环境自动重启，支持实时更新

## 🛠️ 开发指南

### 快速测试新功能

```bash
# 1. 启动服务
source .venv/bin/activate
python main.py

# 2. 测试基础功能
curl http://localhost:8002/api/health
curl -X POST http://localhost:8002/api/chat -H "Content-Type: application/json" -d '{"message": "发布任务失败，请分析原因"}'

# 3. 运行新架构测试
python test_new_agent.py
```

### 高级功能使用

```python
from src.demo.diagnosis_core import DiagnosisService

# 创建服务
service = DiagnosisService(verbose=True)

# 场景切换
service.configure_scenario("compilation_failure")
service.configure_scenario("runtime_failure")

# 模型切换
service.switch_to_real_model(api_key="your-api-key")
service.switch_to_mock_model("k8s_health_check_failure")

# 批量测试所有场景
results = await service.test_all_scenarios("发布任务失败，请分析原因")
```

### 调试模式

```bash
# 启用详细日志
python -c "
from src.demo.diagnosis_core import DiagnosisService
import asyncio

async def debug():
    service = DiagnosisService(verbose=True)
    info = service.get_service_info()
    print('服务信息:', info)

asyncio.run(debug())
"
```

### 添加新的诊断工具

1. 在 `src/core/tools/diagnosis_tools.py` 中添加工具函数
2. 在工具集合中注册新工具
3. 在 `src/core/tools/tool_manager.py` 中更新工具管理
4. 配置场景的工具响应

### 扩展场景配置

详细场景配置指南请参考：[场景配置指南](doc/SCENARIO_GUIDE.md)

```python
# 添加新场景
from src.core.configs.scenarios import ALL_SCENARIOS

custom_scenario = {
    "name": "custom_scenario",
    "description": "自定义场景描述",
    "model": {...},
    "tools": {...}
}

ALL_SCENARIOS["custom_scenario"] = custom_scenario
```

## 📚 详细文档

| 文档 | 描述 |
|------|------|
| [架构重构文档](doc/ARCHITECTURE_REFACTOR.md) | 详细的架构设计和技术实现 |
| [快速开始指南](doc/QUICK_START.md) | 5分钟快速上手指南 |
| [API使用指南](doc/API_GUIDE.md) | 完整的API接口文档 |
| [场景配置指南](doc/SCENARIO_GUIDE.md) | 场景配置和自定义指南 |

## 🔗 项目链接

- **源代码**: [GitHub仓库](https://github.com/your-repo/auto-devops)
- **API文档**: http://localhost:8002/docs (服务启动后访问)
- **架构对比**: [重构前后对比](doc/ARCHITECTURE_REFACTOR.md#重构成果)

## 📄 许可证

MIT License