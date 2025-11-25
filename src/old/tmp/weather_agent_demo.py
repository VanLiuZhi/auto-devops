from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import sys
import os

# 1. 定义工具
@tool
def search_weather(location: str) -> str:
    """Search for weather information in a given location."""
    # 这里应该实现实际的天气搜索逻辑
    # For demo purposes, return a mock response
    return f"The weather in {location} is currently sunny with 25°C"

# 2. 检查是否使用模拟模式
USE_MOCK = os.environ.get('USE_MOCK', '').lower() in ('true', '1', 'yes')

if USE_MOCK:
    print("使用模拟模式（不需要Ollama服务）")

    # 模拟模型类
    class MockModel:
        def invoke(self, messages):
            if isinstance(messages, str):
                query = messages
            elif isinstance(messages, list) and len(messages) > 0:
                query = messages[0].content if hasattr(messages[0], 'content') else str(messages[0])
            else:
                query = str(messages)

            # 模拟简单的响应逻辑
            if "天气" in query:
                if "北京" in query:
                    return "北京的天气是晴天，温度25度"
                elif "上海" in query:
                    return "上海的天气是多云，温度22度"
                else:
                    return f"查询地点的天气是晴天，温度24度"
            elif "距离" in query:
                return "北京到上海的距离大约是1200公里"
            else:
                return "这是一个测试响应"

    model = MockModel()
else:
    # 2. 初始化真实模型
    try:
        model = ChatOllama(model="llama3.2")
        # 测试连接
        print("正在连接Ollama服务...")
        test_response = model.invoke("test")
        print("Ollama服务连接成功")
    except Exception as e:
        print(f"无法连接到Ollama服务: {e}")
        print("请确保Ollama服务正在运行，并且已经安装了llama3.2模型")
        print("启动Ollama服务的命令: ollama serve")
        print("安装llama3.2模型的命令: ollama pull llama3.2")
        print("")
        print("或者使用模拟模式运行:")
        print("set USE_MOCK=true && python weather_agent_demo.py")
        sys.exit(1)

# 3. 创建工具列表
tools = [search_weather]

# 4. 创建智能体
if USE_MOCK:
    # 模拟智能体
    class MockAgent:
        def __init__(self, model, tools):
            self.model = model
            self.tools = tools
            self.tools_dict = {tool.name: tool for tool in tools}

        def invoke(self, input_dict):
            messages = input_dict['messages']
            if isinstance(messages, list) and len(messages) > 0:
                query = messages[0].content if hasattr(messages[0], 'content') else str(messages[0])
            else:
                query = str(messages)

            print(f"\n用户查询: {query}")

            # 检查是否需要使用工具
            response = self.model.invoke(messages)
            print(f"智能体响应: {response}")

            return {'messages': [HumanMessage(content=response)]}

    agent = MockAgent(model, tools)
    print("模拟智能体创建成功")
else:
    try:
        from langgraph.prebuilt import create_react_agent
        agent = create_react_agent(model, tools)
        print("智能体创建成功")
    except ImportError:
        print("无法导入create_react_agent，尝试使用其他方法...")
        # 如果新版本不可用，创建一个简单的代理执行器
        try:
            from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent as langchain_create_react_agent
            from langchain_core.prompts import ChatPromptTemplate

            # 创建prompt模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Use the provided tools to answer questions about weather."),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])

            # 创建agent
            agent_tool = langchain_create_react_agent(model, tools, prompt)
            agent = AgentExecutor(agent=agent_tool, tools=tools, verbose=True)
            print("使用LangChain创建智能体成功")
        except Exception as e:
            print(f"创建智能体失败: {e}")
            sys.exit(1)

# 5. 运行智能体
if __name__ == "__main__":
    # 示例查询
    query = "北京的天气怎么样？"

    # 创建消息
    messages = [HumanMessage(content=query)]

    # 获取智能体响应
    response = agent.invoke({"messages": messages})

    # 打印结果
    print(f"查询: {query}")
    print(f"回复: {response['messages'][-1].content}")

    # 另一个示例查询
    query2 = "上海和北京的天气怎么样？距离有多远？"
    messages2 = [HumanMessage(content=query2)]
    response2 = agent.invoke({"messages": messages2})

    print(f"\n查询: {query2}")
    print(f"回复: {response2['messages'][-1].content}")