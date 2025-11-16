"""
基于Mock框架的天气智能体Demo
展示如何在没有真实大模型的情况下进行完整的开发测试
"""

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from mock_llm_framework import (
    MockConfig, MockChatModel, MockAgent,
    create_mock_weather_tool, create_mock_agent
)


# 1. 定义自定义工具
@tool
def get_travel_distance(city1: str, city2: str) -> str:
    """查询两个城市之间的距离"""
    # 模拟距离数据
    distance_data = {
        ("北京", "上海"): "1200公里",
        ("上海", "北京"): "1200公里",
        ("北京", "广州"): "2100公里",
        ("广州", "北京"): "2100公里",
        ("上海", "广州"): "1400公里",
        ("广州", "上海"): "1400公里",
        ("北京", "深圳"): "2200公里",
        ("深圳", "北京"): "2200公里",
    }

    key = (city1, city2)
    if key in distance_data:
        return f"{city1}到{city2}的距离约为{distance_data[key]}"
    else:
        return f"{city1}到{city2}的距离约为1000公里（模拟数据）"


@tool
def get_weather_advice(location: str, weather_condition: str) -> str:
    """根据天气情况提供穿衣建议"""
    advice_map = {
        "晴天": "建议穿轻便的衣服，可以戴太阳镜",
        "多云": "建议穿长袖衣服，可能需要带伞",
        "雨天": "建议穿防水外套，记得带伞",
        "阴天": "建议穿保暖一些的衣服",
    }

    condition = weather_condition.lower()
    for key in advice_map:
        if key in condition:
            return f"{location}{key}天气：{advice_map[key]}"

    return f"{location}当前天气：建议穿着舒适的服装"


def create_advanced_weather_agent():
    """创建高级天气智能体"""

    # 配置Mock行为
    config = MockConfig(
        response_delay=0.3,  # 300ms延迟模拟真实响应
        use_reasoning=True,  # 显示推理过程
        verbose=True         # 详细日志
    )

    # 准备工具列表
    tools = [
        create_mock_weather_tool(),
        get_travel_distance,
        get_weather_advice
    ]

    # 创建智能体
    agent = create_mock_agent(tools, config)

    return agent


def run_interactive_demo():
    """运行交互式演示"""
    agent = create_advanced_weather_agent()

    print("=" * 60)
    print("Mock天气智能体演示")
    print("=" * 60)
    print("输入 'quit' 退出程序")
    print("输入 'history' 查看工具调用历史")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n用户: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                break

            if user_input.lower() in ['history', '历史']:
                print("\n工具调用历史:")
                history = agent.get_tool_history()
                if not history:
                    print("暂无工具调用记录")
                else:
                    for i, call in enumerate(history, 1):
                        print(f"{i}. 工具: {call['tool']}")
                        print(f"   输入: {call['input']}")
                        print(f"   输出: {call['output']}")
                        print()
                continue

            if not user_input:
                continue

            # 调用智能体
            response = agent.invoke({"messages": [HumanMessage(content=user_input)]})
            answer = response['messages'][0].content
            print(f"\n助手: {answer}")

        except KeyboardInterrupt:
            print("\n\n程序已退出")
            break
        except Exception as e:
            print(f"\n错误: {e}")


def run_batch_demo():
    """运行批量测试演示"""
    agent = create_advanced_weather_agent()

    test_cases = [
        "你好，介绍一下你自己",
        "北京今天天气怎么样？",
        "上海到北京有多远？",
        "广州晴天适合穿什么衣服？",
        "帮我查一下深圳的天气",
        "从上海到广州需要走多远？",
        "杭州阴天有什么建议？"
    ]

    print("=" * 60)
    print("批量测试演示")
    print("=" * 60)

    for i, query in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】")
        print(f"问题: {query}")

        response = agent.invoke({"messages": [HumanMessage(content=query)]})
        answer = response['messages'][0].content
        print(f"回答: {answer}")
        print("-" * 40)

    # 显示统计信息
    history = agent.get_tool_history()
    print(f"\n测试统计:")
    print(f"总问题数: {len(test_cases)}")
    print(f"工具调用次数: {len(history)}")
    print(f"使用的工具: {list(set(call['tool'] for call in history))}")


def test_mock_components():
    """测试Mock框架的各个组件"""
    print("=" * 60)
    print("Mock组件测试")
    print("=" * 60)

    # 测试Mock模型
    print("\n1. 测试Mock模型:")
    model = MockChatModel("test-model")
    test_messages = [
        "你好",
        "北京的天气",
        "普通问题"
    ]

    for msg in test_messages:
        response = model.invoke(msg)
        print(f"输入: {msg} -> 输出: {response.content[:50]}...")

    # 测试Mock工具
    print("\n2. 测试Mock工具:")
    weather_tool = create_mock_weather_tool()
    result = weather_tool.invoke("北京")
    print(f"工具调用结果: {result}")

    # 测试Mock智能体
    print("\n3. 测试Mock智能体:")
    agent = create_mock_agent([weather_tool])
    response = agent.invoke({"messages": [HumanMessage(content="上海天气怎么样？")]})
    print(f"智能体响应: {response['messages'][0].content}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "interactive":
            run_interactive_demo()
        elif mode == "batch":
            run_batch_demo()
        elif mode == "test":
            test_mock_components()
        else:
            print("使用方法:")
            print("  python weather_agent_with_mock.py interactive  # 交互模式")
            print("  python weather_agent_with_mock.py batch       # 批量测试")
            print("  python weather_agent_with_mock.py test        # 组件测试")
    else:
        print("请选择运行模式:")
        print("1. 交互模式 - interactive")
        print("2. 批量测试 - batch")
        print("3. 组件测试 - test")
        print("\n默认运行批量测试...")
        run_batch_demo()