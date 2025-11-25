# diagnosis_core.py
"""
使用LangChain框架实现的故障诊断服务
"""
import time
import asyncio
from typing import Any, List, Optional, Dict, AsyncGenerator

from langchain_core.tools import tool
from langchain_core.language_models.llms import LLM
from langchain.agents import create_agent
import json

# ===============================
# 知识库（从demo复制）
# ===============================
knowledge_base = {
    "健康检查失败": "请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。",
}


# ===============================
# 工具（从demo复制）
# ===============================
@tool
def get_build_log(input_str: str = "") -> str:
    """获取编译构建阶段的日志"""
    time.sleep(1)  # 模拟延迟
    return "[编译阶段日志] Maven 编译成功，没有错误。"


@tool
def get_k8s_log(input_str: str = "") -> str:
    """获取K8s部署阶段的日志"""
    time.sleep(1)
    return "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。"


@tool
def get_service_log(input_str: str = "") -> str:
    """获取服务启动阶段的日志"""
    time.sleep(1)
    return "[服务启动日志] 服务正常启动。"


@tool
def knowledge_lookup(query: str) -> str:
    """从知识库中查找对应的解决方案"""
    time.sleep(1)
    for key, solution in knowledge_base.items():
        if key in query:
            return solution
    return ""


# ===============================
# 简化的工具执行逻辑（暂不使用LangChain Agent）
# ===============================
class SimpleMockAgent:
    """简化的模拟Agent，不依赖复杂的LangChain Agent接口"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.tools = {tool.name: tool for tool in [get_build_log, get_k8s_log, get_service_log, knowledge_lookup]}
        self.max_iterations = 10

    async def stream(self, input_data: dict, stream_mode: str = "updates"):
        """模拟LangChain Agent的stream方法"""
        user_input = input_data["messages"][0]["content"]

        # 发送开始信号
        yield {"model": {"messages": []}}

        # 模拟思考过程
        thoughts = [
            "我需要先获取编译构建日志来分析问题。",
            "现在需要获取K8s部署日志来查看部署情况。",
            "让我获取服务启动日志来了解服务状态。"
        ]

        # 工具调用序列
        tool_calls = [
            {"name": "get_build_log", "args": {"input_str": "_"}},
            {"name": "get_k8s_log", "args": {"input_str": "_"}},
            {"name": "get_service_log", "args": {"input_str": "_"}}
        ]

        # 执行工具调用序列
        for i, (thought, tool_call) in enumerate(zip(thoughts, tool_calls)):
            # 发送思考消息
            yield {"model": {"messages": [{"role": "assistant", "content": thought}]}}

            # 发送工具调用
            yield {"model": {"messages": [{"role": "assistant", "tool_calls": [tool_call]}]}}

            # 执行工具并返回结果
            tool_name = tool_call["name"]
            if tool_name in self.tools:
                try:
                    if tool_name in ["get_build_log", "get_k8s_log", "get_service_log"]:
                        result = self.tools[tool_name].invoke("_")
                    else:
                        result = self.tools[tool_name].invoke(tool_call["args"]["input_str"])

                    yield {"tools": {"messages": [{"name": tool_name, "content": result}]}}
                except Exception as e:
                    yield {"tools": {"messages": [{"name": tool_name, "content": f"工具执行错误: {e}"}]}}

        # 最终分析结果
        final_analysis = """根据日志分析，我发现Pod健康检查失败，端口8080无法访问。这是典型的配置问题。

问题阶段：K8s部署Pod
原因分析：Pod健康检查失败，端口8080无法访问
解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"""

        yield {"model": {"messages": [{"role": "assistant", "content": final_analysis}]}}

    async def invoke(self, input_data: dict) -> dict:
        """模拟LangChain Agent的invoke方法"""
        result_messages = []
        final_result = ""

        async for chunk in self.stream(input_data):
            for step_name, step_data in chunk.items():
                if "messages" in step_data:
                    result_messages.extend(step_data["messages"])

        # 提取最终响应
        for message in reversed(result_messages):
            if hasattr(message, 'content') and message.content and message.content.strip():
                final_result = message.content.strip()
                break
            elif isinstance(message, dict) and message.get("content", "").strip():
                final_result = message["content"].strip()
                break

        return {"messages": result_messages, "final_response": final_result}


# ===============================
# 使用简化Agent的诊断服务
# ===============================
class DiagnosisService:
    """使用简化Agent的故障诊断服务，兼容LangChain风格接口"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.agent = SimpleMockAgent(verbose=verbose)

    async def diagnose_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """流式执行诊断，返回每一步的输出"""

        # 发送开始信号
        yield {"type": "start", "message": "开始故障分析..."}

        try:
            # 使用简化Agent的流式API
            async for chunk in self.agent.stream(
                    {"messages": [{"role": "user", "content": user_input}]},
                    stream_mode="updates"
            ):
                for step_name, step_data in chunk.items():
                    if step_name == "model":
                        # 处理模型响应
                        messages = step_data.get("messages", [])
                        if messages:
                            latest_message = messages[-1]

                            if isinstance(latest_message, dict):
                                content = latest_message.get("content", "")
                                tool_calls = latest_message.get("tool_calls", [])

                                if content:
                                    yield {
                                        "type": "thinking",
                                        "content": content
                                    }

                                if tool_calls:
                                    for tool_call in tool_calls:
                                        yield {
                                            "type": "tool_call",
                                            "tool": tool_call.get("name", ""),
                                            "input": tool_call.get("args", {}),
                                        }

                    elif step_name == "tools":
                        # 处理工具执行结果
                        messages = step_data.get("messages", [])
                        if messages:
                            for message in messages:
                                if isinstance(message, dict):
                                    yield {
                                        "type": "tool_result",
                                        "tool": message.get("name", ""),
                                        "result": message.get("content", "")
                                    }

            # 获取最终结果
            final_result = await self.diagnose(user_input)
            if final_result:
                yield {
                    "type": "final",
                    "content": final_result,
                    "status": "completed"
                }

        except Exception as e:
            yield {
                "type": "error",
                "message": f"诊断过程中出现错误: {str(e)}",
                "status": "failed"
            }

    async def diagnose(self, user_input: str) -> str:
        """同步执行诊断，返回最终结果"""
        try:
            # 使用简化Agent执行诊断
            result = await self.agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            # 提取最终响应
            if result and "final_response" in result:
                return result["final_response"]

            return "未能获得诊断结果，请重试。"

        except Exception as e:
            return f"诊断执行失败: {str(e)}"
