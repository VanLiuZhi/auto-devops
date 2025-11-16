#!/usr/bin/env python3
"""
Mock框架快速启动脚本
一键体验完整的AI智能体开发
"""

import sys
import os
from mock_llm_framework import (
    MockConfig, MockChatModel, MockAgent,
    create_mock_weather_tool, create_mock_agent
)
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage


def demo_basic_usage():
    """演示基础用法"""
    print("=" * 50)
    print("1. 基础用法演示")
    print("=" * 50)

    # 快速创建智能体
    agent = create_mock_agent()

    # 简单对话
    queries = [
        "你好",
        "北京天气怎么样？",
        "介绍一下你自己"
    ]

    for query in queries:
        print(f"\n用户: {query}")
        response = agent.invoke({"messages": [HumanMessage(content=query)]})
        print(f"助手: {response['messages'][0].content}")


def demo_custom_tools():
    """演示自定义工具"""
    print("\n" + "=" * 50)
    print("2. 自定义工具演示")
    print("=" * 50)

    @tool
    def calculate_tip(amount: float, percentage: float = 15.0) -> str:
        """计算小费金额"""
        tip = amount * (percentage / 100)
        total = amount + tip
        return f"账单: ¥{amount:.2f}, 小费({percentage}%): ¥{tip:.2f}, 总计: ¥{total:.2f}"

    @tool
    def translate_text(text: str, target_language: str = "英语") -> str:
        """模拟文本翻译"""
        translations = {
            "英语": f"[English] {text}",
            "日语": f"[日本語] {text}",
            "韩语": f"[한국어] {text}"
        }
        return translations.get(target_language, f"[{target_language}] {text}")

    # 创建带自定义工具的智能体
    agent = create_mock_agent([calculate_tip, translate_text])

    queries = [
        "帮我计算200元账单15%的小费",
        "把'你好世界'翻译成英语",
        "150元账单20%小费是多少？"
    ]

    for query in queries:
        print(f"\n用户: {query}")
        response = agent.invoke({"messages": [HumanMessage(content=query)]})
        print(f"助手: {response['messages'][0].content}")

    print(f"\n工具调用统计:")
    for call in agent.get_tool_history():
        print(f"- {call['tool']}: {call['input']}")


def demo_advanced_config():
    """演示高级配置"""
    print("\n" + "=" * 50)
    print("3. 高级配置演示")
    print("=" * 50)

    # 快速模式（开发用）
    fast_config = MockConfig(
        response_delay=0.1,
        use_reasoning=False,
        verbose=False
    )

    # 演示模式（展示用）
    demo_config = MockConfig(
        response_delay=0.5,
        use_reasoning=True,
        verbose=True
    )

    print("快速模式演示:")
    fast_agent = create_mock_agent(config=fast_config)
    response = fast_agent.invoke({"messages": [HumanMessage(content="快速测试")]})
    print(f"响应: {response['messages'][0].content[:50]}...")

    print("\n演示模式演示:")
    demo_agent = create_mock_agent(config=demo_config)
    response = demo_agent.invoke({"messages": [HumanMessage(content="演示测试")]})
    print(f"响应: {response['messages'][0].content}")


def demo_performance_comparison():
    """演示性能对比"""
    print("\n" + "=" * 50)
    print("4. 性能对比演示")
    print("=" * 50)

    import time

    # Mock模式
    mock_agent = create_mock_agent()
    start_time = time.time()
    mock_agent.invoke({"messages": [HumanMessage(content="测试")]})
    mock_time = time.time() - start_time

    print(f"Mock模式响应时间: {mock_time:.3f}秒")
    print(f"Mock模式成本: ¥0 (免费)")
    print(f"Mock模式可用性: 100% (无依赖)")

    print(f"\n与传统大模型对比:")
    print(f"- 响应速度: 快{1000/mock_time:.0f}倍")
    print(f"- 开发成本: 免费vs付费")
    print(f"- 调试效率: 高（可重现）vs 中（随机性）")


def demo_use_cases():
    """演示使用场景"""
    print("\n" + "=" * 50)
    print("5. 使用场景演示")
    print("=" * 50)

    use_cases = [
        {
            "title": "本地开发",
            "description": "在没有网络的情况下开发AI应用",
            "code": "agent = create_mock_agent()  # 立即可用"
        },
        {
            "title": "单元测试",
            "description": "为AI应用编写可重现的测试用例",
            "code": "response = agent.invoke(test_input)\nassert expected in response"
        },
        {
            "title": "演示原型",
            "description": "快速制作产品演示原型",
            "code": "# 5分钟完成一个智能体原型"
        },
        {
            "title": "教学培训",
            "description": "教授AI应用开发概念",
            "code": "# 学生无需API密钥即可学习"
        }
    ]

    for i, case in enumerate(use_cases, 1):
        print(f"\n{i}. {case['title']}")
        print(f"   用途: {case['description']}")
        print(f"   示例: {case['code']}")


def main():
    """主函数"""
    print("Mock框架快速体验")
    print("在没有大模型的情况下开发AI应用")
    print("https://github.com/your-repo/mock-llm-framework")

    # 检查是否指定了特定演示
    if len(sys.argv) > 1:
        demo = sys.argv[1].lower()
        if demo == "basic":
            demo_basic_usage()
        elif demo == "tools":
            demo_custom_tools()
        elif demo == "config":
            demo_advanced_config()
        elif demo == "performance":
            demo_performance_comparison()
        elif demo == "cases":
            demo_use_cases()
        else:
            print("可用的演示:")
            print("- basic: 基础用法")
            print("- tools: 自定义工具")
            print("- config: 高级配置")
            print("- performance: 性能对比")
            print("- cases: 使用场景")
    else:
        # 运行所有演示
        demo_basic_usage()
        demo_custom_tools()
        demo_advanced_config()
        demo_performance_comparison()
        demo_use_cases()

    print("\n" + "=" * 50)
    print("演示完成！")
    print("\n下一步:")
    print("1. 阅读 MOCK_DEVELOPMENT_GUIDE.md 了解详细用法")
    print("2. 运行 python weather_agent_with_mock.py 体验完整示例")
    print("3. 开始构建你自己的AI应用！")
    print("=" * 50)


if __name__ == "__main__":
    main()