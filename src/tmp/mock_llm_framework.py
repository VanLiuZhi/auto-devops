"""
Mock LLM Framework - 用于在没有大模型的情况下开发和测试LangChain/LangGraph应用
提供完整的模拟环境，支持工具调用、智能体推理等核心功能
"""

import json
import re
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool


@dataclass
class MockConfig:
    """Mock配置类"""
    response_delay: float = 0.1  # 模拟响应延迟（秒）
    use_reasoning: bool = True   # 是否启用推理步骤显示
    verbose: bool = True         # 是否显示详细信息
    default_model: str = "mock-gpt-4"


class MockChatModel:
    """模拟大语言模型类"""

    def __init__(self, model_name: str = "mock-gpt-4", config: Optional[MockConfig] = None):
        self.model_name = model_name
        self.config = config or MockConfig()
        self.call_count = 0

        # 预定义的响应模板
        self.response_templates = {
            "greeting": [
                "你好！我是AI助手，很高兴为您服务。",
                "您好！有什么可以帮助您的吗？",
                "Hello! How can I assist you today?"
            ],
            "weather_query": [
                "我需要使用天气搜索工具来查询天气信息。",
                "让我为您查询相关的天气情况。",
                "我调用天气工具来获取准确的天气信息。"
            ],
            "tool_result": [
                "根据工具返回的结果，我为您提供以下信息。",
                "基于工具查询结果，我可以告诉您：",
                "工具返回了以下信息："
            ],
            "default": [
                "我理解您的请求，让我为您提供帮助。",
                "这是一个很好的问题，我来为您解答。",
                "我明白您的需求，让我处理一下。"
            ]
        }

    def _analyze_message(self, message: Union[str, List[BaseMessage]]) -> Dict[str, Any]:
        """分析用户消息，提取意图和参数"""
        if isinstance(message, str):
            content = message
        elif isinstance(message, list) and len(message) > 0:
            content = message[0].content if hasattr(message[0], 'content') else str(message[0])
        else:
            content = str(message)

        # 简单的意图识别
        intent = "default"
        location = None

        if any(word in content.lower() for word in ["天气", "weather", "气温", "温度"]):
            intent = "weather_query"
            # 提取地名
            location_patterns = [
                r"(北京|上海|广州|深圳|杭州|成都|武汉|西安|南京|重庆)",
                r"(.{2,4})的天气",
                r"weather in ([a-zA-Z\s]+)"
            ]
            for pattern in location_patterns:
                match = re.search(pattern, content)
                if match:
                    location = match.group(1) or match.group(2)
                    break

        if any(word in content.lower() for word in ["你好", "hello", "hi", "您好"]):
            intent = "greeting"

        return {
            "content": content,
            "intent": intent,
            "location": location,
            "needs_tools": intent == "weather_query"
        }

    def _generate_response(self, analysis: Dict[str, Any]) -> str:
        """生成模拟响应"""
        intent = analysis["intent"]

        if intent in self.response_templates:
            import random
            response = random.choice(self.response_templates[intent])
        else:
            response = "我理解您的请求，正在处理中..."

        # 根据分析结果调整响应
        if analysis.get("location"):
            response += f" 查询地点：{analysis['location']}"

        return response

    def invoke(self, messages: Union[str, List[BaseMessage]]) -> AIMessage:
        """模拟模型调用"""
        self.call_count += 1

        import time
        time.sleep(self.config.response_delay)

        analysis = self._analyze_message(messages)
        content = self._generate_response(analysis)

        if self.config.verbose:
            print(f"[Mock Model] 调用次数: {self.call_count}")
            print(f"[Mock Model] 分析结果: {analysis}")
            print(f"[Mock Model] 生成响应: {content}")

        return AIMessage(content=content)


class MockTool:
    """模拟工具类"""

    def __init__(self, name: str, description: str, func=None):
        self.name = name
        self.description = description
        self.func = func
        self.call_count = 0

    def invoke(self, input_data: Any) -> str:
        """模拟工具调用"""
        self.call_count += 1

        if self.func:
            return self.func(input_data)
        else:
            # 默认模拟响应
            return f"[Mock Tool {self.name}] 处理输入: {input_data} (第{self.call_count}次调用)"


class MockAgent:
    """模拟智能体类"""

    def __init__(self, model: MockChatModel, tools: List[BaseTool], config: Optional[MockConfig] = None):
        self.model = model
        self.tools = tools
        self.config = config or MockConfig()
        self.tool_history = []

        # 创建工具映射
        self.tools_dict = {tool.name: tool for tool in tools}

    def _should_use_tool(self, message: str) -> bool:
        """判断是否需要使用工具"""
        tool_keywords = ["天气", "查询", "搜索", "weather", "search", "find"]
        return any(keyword in message.lower() for keyword in tool_keywords)

    def _select_tool(self, message: str) -> Optional[BaseTool]:
        """选择合适的工具"""
        message_lower = message.lower()

        for tool in self.tools:
            if hasattr(tool, 'name'):
                if "weather" in tool.name.lower() and "天气" in message_lower:
                    return tool
                elif "weather" in tool.name.lower() and "weather" in message_lower:
                    return tool

        # 如果没有明确匹配，返回第一个工具
        return self.tools[0] if self.tools else None

    def _execute_tool(self, tool: BaseTool, input_data: str) -> str:
        """执行工具调用"""
        if self.config.verbose:
            print(f"[Mock Agent] 调用工具: {tool.name}")
            print(f"[Mock Agent] 工具输入: {input_data}")

        try:
            if hasattr(tool, 'invoke'):
                result = tool.invoke(input_data)
            else:
                result = tool.run(input_data)

            self.tool_history.append({
                "tool": tool.name,
                "input": input_data,
                "output": result
            })

            if self.config.verbose:
                print(f"[Mock Agent] 工具输出: {result}")

            return result
        except Exception as e:
            error_msg = f"工具执行错误: {e}"
            if self.config.verbose:
                print(f"[Mock Agent] {error_msg}")
            return error_msg

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """模拟智能体调用"""
        messages = input_dict.get('messages', [])
        if not messages:
            return {"messages": [AIMessage(content="没有收到输入消息")]}

        # 提取用户消息
        if isinstance(messages, list) and len(messages) > 0:
            user_message = messages[0].content if hasattr(messages[0], 'content') else str(messages[0])
        else:
            user_message = str(messages)

        if self.config.verbose:
            print(f"\n{'='*50}")
            print(f"[Mock Agent] 收到查询: {user_message}")
            print(f"{'='*50}")

        # 1. 模型思考
        model_response = self.model.invoke(messages)

        # 2. 判断是否需要使用工具
        if self._should_use_tool(user_message):
            selected_tool = self._select_tool(user_message)
            if selected_tool:
                # 提取工具参数（这里简单模拟）
                tool_input = user_message

                # 执行工具
                tool_result = self._execute_tool(selected_tool, tool_input)

                # 生成最终响应
                final_response = f"{model_response.content}\n\n查询结果：{tool_result}"
            else:
                final_response = f"{model_response.content}\n\n抱歉，没有找到合适的工具来处理您的请求。"
        else:
            final_response = model_response.content

        # 返回结果
        response_message = AIMessage(content=final_response)

        if self.config.verbose:
            print(f"[Mock Agent] 最终响应: {final_response}")
            print(f"{'='*50}\n")

        return {"messages": [response_message]}

    def get_tool_history(self) -> List[Dict[str, Any]]:
        """获取工具调用历史"""
        return self.tool_history.copy()


def create_mock_weather_tool():
    """创建模拟天气工具"""
    @tool
    def search_weather(location: str) -> str:
        """模拟天气查询工具"""
        weather_data = {
            "北京": {"temperature": "25°C", "condition": "晴天", "humidity": "45%"},
            "上海": {"temperature": "22°C", "condition": "多云", "humidity": "65%"},
            "广州": {"temperature": "28°C", "condition": "阵雨", "humidity": "75%"},
            "深圳": {"temperature": "27°C", "condition": "晴天", "humidity": "70%"},
            "杭州": {"temperature": "24°C", "condition": "阴天", "humidity": "60%"},
        }

        if location in weather_data:
            data = weather_data[location]
            return f"{location}当前天气：{data['condition']}，温度{data['temperature']}，湿度{data['humidity']}"
        else:
            return f"抱歉，暂时没有{location}的天气信息。模拟数据：晴天，温度24°C，湿度55%"

    return search_weather


def create_mock_agent(tools: List[BaseTool] = None, config: MockConfig = None) -> MockAgent:
    """快速创建模拟智能体"""
    if tools is None:
        tools = [create_mock_weather_tool()]

    model = MockChatModel(config=config)
    agent = MockAgent(model, tools, config=config)

    return agent


# 使用示例
if __name__ == "__main__":
    # 创建配置
    config = MockConfig(
        response_delay=0.5,
        use_reasoning=True,
        verbose=True
    )

    # 创建工具
    weather_tool = create_mock_weather_tool()

    # 创建智能体
    agent = create_mock_agent([weather_tool], config)

    # 测试查询
    test_queries = [
        "你好",
        "北京的天气怎么样？",
        "上海和杭州的天气如何？",
        "今天深圳热不热？"
    ]

    for query in test_queries:
        response = agent.invoke({"messages": [HumanMessage(content=query)]})
        print(f"用户: {query}")
        print(f"助手: {response['messages'][0].content}")
        print("-" * 40)

    # 显示工具调用历史
    print("工具调用历史:")
    for i, call in enumerate(agent.get_tool_history(), 1):
        print(f"{i}. 工具: {call['tool']}, 输入: {call['input']}, 输出: {call['output'][:50]}...")