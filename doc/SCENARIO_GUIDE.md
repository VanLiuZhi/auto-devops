# 场景配置指南

## 📋 概述

Auto DevOps 支持通过场景配置来模拟各种故障诊断情况。场景配置允许您精确控制模型的响应序列和工具返回结果，用于测试和验证诊断系统的行为。

## 🎯 场景配置作用

- **测试验证**: 验证Agent在不同情况下的行为
- **功能演示**: 演示特定的故障诊断流程
- **开发调试**: 在开发过程中模拟特定问题
- **性能测试**: 测试复杂场景下的系统性能

## 🏗️ 场景配置结构

### 完整场景配置

```python
scenario_config = {
    "name": "场景名称",
    "description": "场景描述",
    "expected_steps": ["预期步骤1", "预期步骤2"],
    "expected_result": "预期结果描述",

    # 模型配置
    "model": {
        "name": "模型内部名称",
        "sequence": [
            {
                "type": "thought|action|final",
                "content": "思考内容（thought类型）",
                "tool": "工具名称（action类型）",
                "input": "工具参数（action类型）"
            }
        ]
    },

    # 工具配置
    "tools": {
        "build_log": "编译日志内容",
        "k8s_log": "K8s部署日志内容",
        "service_log": "服务启动日志内容",
        "knowledge_base": {
            "关键词": "解决方案内容"
        }
    }
}
```

### 配置字段说明

#### Model 配置

**type 字段类型**:
- `thought`: AI的思考过程，纯文本输出
- `action`: 调用工具，需要配合 `tool` 和 `input` 字段
- `final`: 最终结论，诊断流程结束

**action 类型示例**:
```python
{
    "type": "action",
    "tool": "get_build_log",
    "input": "_"
}
```

#### Tools 配置

**基础工具**:
- `build_log`: 编译构建阶段的日志
- `k8s_log`: Kubernetes部署阶段的日志
- `service_log`: 服务启动阶段的日志
- `knowledge_base`: 知识库查询结果

## 📚 预定义场景详解

### 1. K8s健康检查失败场景

```python
K8S_HEALTH_CHECK_FAILURE = {
    "name": "k8s_health_check_failure",
    "description": "K8s健康检查失败场景 - 最常见的发布问题",
    "expected_steps": [
        "获取编译日志",
        "获取K8s部署日志",
        "发现健康检查失败",
        "获取服务启动日志",
        "查询知识库解决方案"
    ],
    "expected_result": "端口配置不一致的健康检查失败",

    "model": {
        "sequence": [
            {"type": "thought", "content": "发布任务失败了，让我先检查编译构建日志。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译没问题，现在检查K8s部署日志。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "发现了问题！Pod健康检查失败，端口8080无法访问。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "需要查询知识库获取解决方案。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "健康检查失败"},
            {"type": "final", "content": "问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译成功，没有错误。",
        "k8s_log": "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。",
        "service_log": "[服务启动日志] 服务正常启动。",
        "knowledge_base": {
            "健康检查失败": "请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
        }
    }
}
```

### 2. 编译失败场景

```python
COMPILATION_FAILURE = {
    "name": "compilation_failure",
    "description": "编译失败场景 - Maven构建问题",

    "model": {
        "sequence": [
            {"type": "thought", "content": "发布任务失败，让我先检查编译构建日志。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "发现了编译错误！Maven构建失败，依赖项缺失。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "编译失败"},
            {"type": "final", "content": "问题阶段：编译构建\n原因分析：Maven编译失败，依赖项缺失或版本冲突\n解决方案：请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译失败！[ERROR] Failed to execute goal on project: Could not resolve dependencies...",
        "k8s_log": "[部署阶段日志] 未执行，因为编译失败。",
        "service_log": "[服务启动日志] 未执行，因为编译失败。",
        "knowledge_base": {
            "编译失败": "请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。"
        }
    }
}
```

### 3. 运行时错误场景

```python
RUNTIME_FAILURE = {
    "name": "runtime_failure",
    "description": "运行时错误场景 - 服务启动后出现异常",

    "model": {
        "sequence": [
            {"type": "thought", "content": "发布任务失败，让我按步骤检查。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译正常，检查K8s部署。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "部署也成功了，检查服务启动日志。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "发现了运行时错误！服务启动后出现NullPointerException。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "运行时错误"},
            {"type": "final", "content": "问题阶段：服务运行\n原因分析：服务启动后出现NullPointerException，可能是配置缺失或空引用\n解决方案：请检查服务启动日志中的详细错误堆栈，确认相关配置文件是否存在且格式正确，检查代码中的空值处理逻辑。"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译成功，没有错误。",
        "k8s_log": "[部署阶段日志] Helm 部署成功。",
        "service_log": "[服务启动日志] 服务启动失败！java.lang.NullPointerException: Cannot invoke \"String.length()\" because \"str\" is null",
        "knowledge_base": {
            "运行时错误": "请检查服务启动日志中的详细错误堆栈，确认相关配置文件是否存在且格式正确，检查代码中的空值处理逻辑。"
        }
    }
}
```

## 🛠️ 创建自定义场景

### 方法1：直接代码配置

```python
from src.demo.diagnosis_core import DiagnosisService

# 创建自定义场景
custom_scenario = {
    "name": "database_connection_error",
    "description": "数据库连接错误场景",

    "model": {
        "sequence": [
            {"type": "thought", "content": "用户报告服务无法启动，可能是数据库问题。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译正常，检查部署情况。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "部署也成功，检查服务日志。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "发现数据库连接失败！查询解决方案。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "数据库连接"},
            {"type": "final", "content": "问题阶段：服务启动\n原因分析：数据库连接失败，可能是数据库服务未启动或连接配置错误\n解决方案：检查数据库服务状态，确认数据库连接参数和凭据配置正确。"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] 编译成功！",
        "k8s_log": "[部署阶段日志] 部署成功！",
        "service_log": "[服务启动日志] Database connection failed: Connection refused to localhost:5432",
        "knowledge_base": {
            "数据库连接": "检查数据库服务是否运行，确认连接字符串、用户名、密码配置正确，检查网络连接和防火墙设置。"
        }
    }
}

# 应用自定义场景
from src.core.configs.scenarios import ALL_SCENARIOS
ALL_SCENARIOS["database_connection_error"] = custom_scenario

# 使用场景
service = DiagnosisService()
service.configure_scenario("database_connection_error")
result = await service.diagnose("服务无法启动")
```

### 方法2：扩展场景文件

```python
# 在 src/core/configs/scenarios.py 中添加

NEW_CUSTOM_SCENARIO = {
    "name": "api_gateway_error",
    "description": "API网关错误场景",

    "model": {
        "sequence": [
            {"type": "thought", "content": "用户报告API调用失败，检查日志。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "action", "tool": "knowledge_lookup", "input": "API网关"},
            {"type": "final", "content": "问题阶段：API网关配置\n原因分析：API网关路由配置错误或后端服务不可用\n解决方案：检查API网关路由规则，确认后端服务正常运行，检查网络连接配置。"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] 编译成功！",
        "k8s_log": "[部署阶段日志] 部署成功！",
        "service_log": "[服务启动日志] API Gateway Error: Route not found for path /api/users",
        "knowledge_base": {
            "API网关": "检查路由配置规则，确认后端服务可访问性，验证请求路径和参数格式。"
        }
    }
}

# 添加到场景集合
ALL_SCENARIOS["api_gateway_error"] = NEW_CUSTOM_SCENARIO
```

## 🎨 场景设计最佳实践

### 1. 逻辑真实性

```python
# 好的实践
"sequence": [
    {"type": "thought", "content": "开始分析问题，先检查编译状态。"},
    {"type": "action", "tool": "get_build_log", "input": "_"},
    {"type": "thought", "content": "编译正常，继续检查部署状态。"},
    # ... 合理的诊断流程
]

# 避免的实践
"sequence": [
    {"type": "action", "tool": "get_build_log", "input": "_"},  # 缺少思考过程
    {"type": "action", "tool": "final_answer", "input": "_"},  # 跳过必要步骤
]
```

### 2. 工具使用规范

```python
# 正确的工具调用
{"type": "action", "tool": "get_build_log", "input": "_"}

# 知识库查询
{"type": "action", "tool": "knowledge_lookup", "input": "包含关键词的查询内容"}
```

### 3. 日志内容真实感

```python
# 真实的日志格式
"build_log": "[编译阶段日志] Maven 编译失败！\n[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.8.1:compile on project my-app:1.0.0: Compilation failure\n[ERROR] /path/to/File.java:[10,40] error: cannot find symbol\n[ERROR]     symbol: class SomeClass"

# 避免过于简单的日志
"build_log": "编译失败"  # 信息量太少
```

### 4. 错误描述详细

```python
# 好的最终结果
"final": "问题阶段：服务启动\n原因分析：NullPointerException发生在配置加载时，因为配置文件中缺少必需的数据库连接参数\n解决方案：检查application.yml或application.properties文件，确保包含正确的数据库连接URL、用户名、密码配置，验证数据库服务可访问性。"

# 避免过于简化的结论
"final": "配置文件问题"  # 信息量不足
```

## 🧪 场景测试

### 基础测试脚本

```python
import asyncio
from src.demo.diagnosis_core import DiagnosisService

async def test_custom_scenario():
    # 创建服务
    service = DiagnosisService(verbose=True)

    # 测试场景
    scenarios_to_test = [
        "k8s_health_check_failure",
        "compilation_failure",
        "runtime_failure",
        "custom_scenario_name"
    ]

    test_input = "服务部署失败，请分析原因"

    for scenario_name in scenarios_to_test:
        print(f"\n=== 测试场景: {scenario_name} ===")

        # 配置场景
        service.configure_scenario(scenario_name)

        # 获取场景信息
        info = service.get_service_info()
        print(f"当前场景: {info['current_scenario']}")

        # 执行诊断
        result = await service.diagnose(test_input)
        print(f"诊断结果: {result[:100]}...")

        # 流式诊断查看步骤
        print("执行步骤:")
        step_count = 0
        async for chunk in service.diagnose_stream(test_input):
            if chunk["type"] in ["tool_call", "tool_result"]:
                step_count += 1
                print(f"  {step_count}. {chunk['type']}: {chunk.get('tool', '')}")

        print(f"总步骤数: {step_count}")

# 运行测试
asyncio.run(test_custom_scenario())
```

### 批量场景验证

```python
async def validate_all_scenarios():
    service = DiagnosisService()

    # 测试所有预定义场景
    results = await service.test_all_scenarios("发布任务失败，请分析原因")

    print("=== 场景测试结果 ===")
    for scenario_name, result in results.items():
        status = "✅ 成功" if result.get("success") else "❌ 失败"
        steps = result.get("total_steps", 0)
        print(f"{scenario_name:25}: {status} (步骤: {steps})")

        if not result.get("success"):
            print(f"  错误: {result.get('error')}")

asyncio.run(validate_all_scenarios())
```

## 📋 场景清单

### 常见场景类型

1. **基础设施问题**
   - K8s健康检查失败
   - 资源限制（CPU/内存不足）
   - 网络连接问题

2. **构建问题**
   - 编译错误
   - 依赖项冲突
   - 构建工具错误

3. **部署问题**
   - 镜像拉取失败
   - 配置映射错误
   - 环境变量问题

4. **运行时问题**
   - 数据库连接失败
   - 服务依赖不可用
   - 配置文件错误

5. **性能问题**
   - 内存泄漏
   - CPU使用率过高
   - 响应时间过长

## 🔧 场景调试技巧

### 1. 启用详细日志

```python
service = DiagnosisService(verbose=True)
service.configure_scenario("your_scenario")

# 查看详细执行过程
async for chunk in service.diagnose_stream("测试问题"):
    print(f"{chunk['type']}: {chunk}")
```

### 2. 单步调试

```python
# 暂停在特定步骤
service.configure_scenario("debug_scenario")

# 手动测试工具调用
from src.core.tools.tool_manager import tool_manager

result = tool_manager.invoke_tool("get_build_log", "_")
print(f"工具结果: {result}")
```

### 3. 验证场景一致性

```python
# 确保模型和工具配置一致
scenario = get_scenario("your_scenario")

# 检查模型sequence长度
model_steps = len([s for s in scenario["model"]["sequence"]
                    if s["type"] == "action"])

# 检查工具配置完整性
required_tools = {"build_log", "k8s_log", "service_log", "knowledge_base"}
available_tools = scenario["tools"].keys()

print(f"模型步骤数: {model_steps}")
print(f"可用工具: {available_tools}")
print(f"缺失工具: {required_tools - available_tools}")
```

---

🎯 **通过合理配置场景，可以全面测试和验证诊断系统的能力！**