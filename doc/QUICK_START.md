# 快速开始指南

## 🚀 5分钟快速体验

### 1. 启动服务
```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动服务
python main.py
```

### 2. 测试基础功能
```bash
# 健康检查
curl http://localhost:8002/api/health

# 同步诊断
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}'

# 流式诊断
curl -X POST http://localhost:8002/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "发布任务失败，请分析原因"}' --no-buffer
```

### 3. 运行完整测试
```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行新架构测试
python test_new_agent.py
```

## 🧪 场景测试

### Python 代码示例

```python
import asyncio
from src.demo.diagnosis_core import DiagnosisService

async def demo():
    # 创建诊断服务
    service = DiagnosisService(verbose=True)

    # 测试不同场景
    scenarios = [
        "k8s_health_check_failure",
        "compilation_failure",
        "runtime_failure",
        "normal_flow"
    ]

    for scenario in scenarios:
        print(f"\n=== 测试场景: {scenario} ===")

        # 配置场景
        service.configure_scenario(scenario)

        # 执行诊断
        result = await service.diagnose("发布任务失败，请分析原因")
        print(f"结果: {result[:100]}...")

        # 流式诊断（显示步骤）
        print("步骤:")
        async for chunk in service.diagnose_stream("发布任务失败，请分析原因"):
            if chunk["type"] == "tool_call":
                print(f"  🔧 {chunk['tool']}")
            elif chunk["type"] == "final":
                print(f"  ✅ 完成")

# 运行演示
asyncio.run(demo())
```

## 🔧 高级配置

### 场景切换
```python
service = DiagnosisService()

# 切换到编译失败场景
service.configure_scenario("compilation_failure")

# 切换到运行时错误场景
service.configure_scenario("runtime_failure")

# 查看当前配置
info = service.get_service_info()
print(f"当前场景: {info['current_scenario']}")
```

### 模型切换
```python
# 切换到真实GLM模型
service.switch_to_real_model(api_key="your-api-key")

# 切换回Mock模型
service.switch_to_mock_model("k8s_health_check_failure")

# 测试所有场景
results = await service.test_all_scenarios("发布任务失败，请分析原因")
for scenario, result in results.items():
    status = "✅" if result['success'] else "❌"
    print(f"{scenario}: {status}")
```

## 📋 可用场景

| 场景名称 | 描述 | 预期结果 |
|---------|------|----------|
| `k8s_health_check_failure` | K8s健康检查失败 | 端口配置问题 |
| `compilation_failure` | 编译失败 | 依赖项缺失或版本冲突 |
| `runtime_failure` | 运行时错误 | 配置缺失或空引用 |
| `multi_step_complex` | 复杂多步骤问题 | 资源配置和依赖问题 |
| `normal_flow` | 正常流程 | 实际发布成功 |

## 🏗️ 架构概览

```
FastAPI接口层
    ↓
服务适配层 (diagnosis_core.py)
    ↓
Agent执行层 (diagnosis_agent.py + react_executor.py)
    ↓
模型工具层 (models/ + tools/)
    ↓
配置管理层 (configs/)
```

## 🔍 故障排查

### 常见问题

**Q: 流式接口只显示开始和结束，没有中间步骤**
A: 检查MockLLM的场景配置，确保sequence中的action类型正确

**Q: 真实模型无法工作**
A: 检查GLM API密钥配置，确保网络连接正常

**Q: 场景切换无效**
A: 确认场景名称在预定义列表中，或检查自定义场景格式

**Q: 工具调用返回错误**
A: 检查工具场景配置，确保工具响应格式正确

### 调试技巧

```python
# 启用详细日志
service = DiagnosisService(verbose=True)

# 查看Agent状态
info = service.get_service_info()
print(json.dumps(info, indent=2, ensure_ascii=False))

# 手动测试单个工具
from src.core.tools.tool_manager import tool_manager
result = tool_manager.invoke_tool("get_build_log", "_")
print(f"工具结果: {result}")
```

## 📚 详细文档

- **架构设计**: [ARCHITECTURE_REFACTOR.md](ARCHITECTURE_REFACTOR.md)
- **源码目录**: `src/core/` (新架构) 和 `src/demo/` (兼容层)
- **配置示例**: `src/core/configs/` (场景和配置)
- **测试脚本**: `test_new_agent.py` (完整测试)

## 🎯 最佳实践

### 开发建议
1. **先测试Mock模型**: 确保场景配置正确
2. **逐步切换**: 先测试简单场景，再测试复杂场景
3. **日志调试**: 启用verbose模式查看详细执行过程
4. **场景验证**: 每个场景都要测试工具调用和最终结果

### 生产部署
1. **使用真实模型**: 配置GLM API密钥
2. **性能优化**: 调整max_iterations参数
3. **监控告警**: 添加API调用监控
4. **错误处理**: 完善异常处理和降级机制

---

🚀 **开始使用新架构，享受标准化ReAct流程带来的强大功能！**