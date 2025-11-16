# Mock框架开发指南

## 📖 概述

这个Mock框架专为LangChain/LangGraph开发者设计，让你在没有真实大模型的情况下进行完整的AI应用开发和测试。

## 🚀 快速开始

### 1. 基础使用

```python
from mock_llm_framework import create_mock_agent

# 快速创建一个带天气工具的智能体
agent = create_mock_agent()

# 使用智能体
response = agent.invoke({
    "messages": [HumanMessage(content="北京天气怎么样？")]
})
print(response['messages'][0].content)
```

### 2. 自定义配置

```python
from mock_llm_framework import MockConfig, create_mock_agent

# 自定义配置
config = MockConfig(
    response_delay=0.5,    # 模拟响应延迟（秒）
    use_reasoning=True,    # 显示推理过程
    verbose=True          # 详细日志
)

agent = create_mock_agent(config=config)
```

### 3. 添加自定义工具

```python
from langchain_core.tools import tool
from mock_llm_framework import MockAgent, MockChatModel, MockConfig

@tool
def my_custom_tool(input_data: str) -> str:
    """自定义工具示例"""
    return f"处理结果: {input_data}"

# 创建智能体
model = MockChatModel(config=config)
agent = MockAgent(model, [my_custom_tool], config=config)
```

## 🔧 核心组件

### MockChatModel

模拟大语言模型，支持：
- 意图识别（天气查询、问候、一般问题）
- 生成自然语言响应
- 模拟响应延迟
- 调用统计

```python
from mock_llm_framework import MockChatModel

model = MockChatModel("gpt-4")
response = model.invoke("你好")
print(response.content)
```

### MockAgent

模拟智能体，支持：
- 工具选择和调用
- 推理步骤模拟
- 工具调用历史记录
- 多轮对话

```python
from mock_llm_framework import MockAgent

agent = MockAgent(model, tools, config)
response = agent.invoke({"messages": messages})
history = agent.get_tool_history()
```

### MockTool

模拟工具类，支持：
- 调用统计
- 自定义响应逻辑
- 错误处理

## 📋 开发工作流

### 1. 本地开发阶段

```python
# 使用Mock进行开发
agent = create_mock_agent(config=MockConfig(verbose=True))

# 测试业务逻辑
test_cases = [
    "查询天气",
    "计算距离",
    "获取建议"
]

for query in test_cases:
    response = agent.invoke({"messages": [HumanMessage(content=query)]})
    # 验证响应逻辑
    validate_response(response)
```

### 2. 集成测试阶段

```python
# Mock模式测试
mock_agent = create_mock_agent()
run_integration_tests(mock_agent)

# 真实模型测试
if os.environ.get('USE_REAL_MODEL'):
    real_agent = create_real_agent()
    compare_results(mock_agent, real_agent)
```

### 3. 生产部署

```python
# 环境变量控制
USE_MOCK = os.environ.get('USE_MOCK', 'false').lower() == 'true'

if USE_MOCK:
    agent = create_mock_agent()
else:
    agent = create_production_agent()
```

## 🎯 最佳实践

### 1. 工具设计

```python
# 好的实践：明确的输入输出
@tool
def search_weather(location: str) -> str:
    """
    查询指定地点的天气信息

    Args:
        location: 城市名称，如"北京"、"上海"

    Returns:
        天气信息字符串
    """
    # 实现逻辑
    return f"{location}的天气信息"

# 好的实践：错误处理
@tool
def calculate_distance(city1: str, city2: str) -> str:
    """计算两个城市之间的距离"""
    try:
        # 实际计算逻辑
        return f"{city1}到{city2}的距离: {distance}公里"
    except Exception as e:
        return f"距离计算失败: {e}"
```

### 2. 智能体配置

```python
# 开发阶段：详细日志
dev_config = MockConfig(
    response_delay=0.1,
    use_reasoning=True,
    verbose=True
)

# 测试阶段：快速执行
test_config = MockConfig(
    response_delay=0.0,
    use_reasoning=False,
    verbose=False
)

# 演示阶段：模拟真实
demo_config = MockConfig(
    response_delay=1.0,
    use_reasoning=True,
    verbose=False
)
```

### 3. 测试策略

```python
def test_weather_agent():
    """测试天气智能体的完整流程"""
    agent = create_mock_agent()

    # 测试用例
    test_cases = [
        {
            "input": "北京天气怎么样？",
            "expected_contains": ["北京", "天气"],
            "should_call_tool": True
        },
        {
            "input": "你好",
            "expected_contains": ["你好", "AI"],
            "should_call_tool": False
        }
    ]

    for case in test_cases:
        response = agent.invoke({"messages": [HumanMessage(content=case["input"])]})

        # 验证响应内容
        for keyword in case["expected_contains"]:
            assert keyword in response['messages'][0].content

        # 验证工具调用
        if case["should_call_tool"]:
            assert len(agent.get_tool_history()) > 0
```

## 🔍 调试技巧

### 1. 详细日志

```python
config = MockConfig(
    verbose=True  # 显示所有推理过程
)
```

### 2. 工具调用历史

```python
# 查看所有工具调用
history = agent.get_tool_history()
for i, call in enumerate(history, 1):
    print(f"{i}. 工具: {call['tool']}")
    print(f"   输入: {call['input']}")
    print(f"   输出: {call['output']}")
```

### 3. 响应分析

```python
# 分析模型行为
model = MockChatModel()
model.invoke("测试消息")

# 查看调用次数
print(f"模型调用次数: {model.call_count}")
```

## 📊 性能对比

| 指标 | Mock模式 | 真实模型 | 优势 |
|------|----------|----------|------|
| 响应时间 | < 100ms | 1-10秒 | 快100倍 |
| 成本 | 免费 | $0.01-0.10/请求 | 零成本 |
| 可用性 | 100% | 依赖网络 | 稳定 |
| 一致性 | 100% | 变化 | 可预测 |
| 开发效率 | 高 | 中 | 快速迭代 |

## 🚀 迁移指南

### 从Mock到生产

1. **保持接口一致**
```python
# Mock版本
mock_agent = create_mock_agent()

# 生产版本（相同接口）
real_agent = create_real_agent()

# 使用相同的调用方式
response = agent.invoke({"messages": messages})
```

2. **渐进式迁移**
```python
def get_agent():
    if is_development():
        return create_mock_agent()
    elif is_testing():
        return create_staging_agent()
    else:
        return create_production_agent()
```

3. **A/B测试**
```python
def handle_request(request):
    if random.random() < 0.1:  # 10%流量到真实模型
        response = real_agent.invoke(request)
        log_comparison(mock_response, response)
        return response
    else:
        return mock_agent.invoke(request)
```

## 🎮 交互模式

```bash
# 启动交互式Demo
python weather_agent_with_mock.py interactive

# 批量测试
python weather_agent_with_mock.py batch

# 组件测试
python weather_agent_with_mock.py test
```

## 📝 扩展Mock框架

### 自定义响应生成

```python
class CustomMockModel(MockChatModel):
    def _generate_response(self, analysis):
        # 自定义响应生成逻辑
        if analysis["intent"] == "custom_intent":
            return "自定义响应"
        return super()._generate_response(analysis)
```

### 添加新的工具类型

```python
def create_database_tool():
    @tool
    def query_database(sql: str) -> str:
        """模拟数据库查询"""
        return f"查询结果: {sql} -> 模拟数据"

    return query_database
```

## 🛠️ 故障排除

### 常见问题

1. **编码错误**
```python
# 问题：Windows控制台编码
# 解决：使用UTF-8编码或避免特殊字符
```

2. **工具不被调用**
```python
# 检查关键词匹配
config = MockConfig(verbose=True)  # 启用详细日志
```

3. **响应不符合预期**
```python
# 自定义响应模板
model.response_templates["custom"] = ["自定义响应1", "自定义响应2"]
```

## 📚 参考资料

- [LangChain官方文档](https://python.langchain.com/)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [本项目的CLAUDE.md](./CLAUDE.md)

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进Mock框架！

### 贡献方向
- 新的工具类型
- 更智能的响应生成
- 更好的意图识别
- 性能优化
- 文档改进

---

*这个Mock框架让你能够在没有大模型的情况下进行完整的AI应用开发，大大提高开发效率并降低成本。*