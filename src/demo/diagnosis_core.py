# diagnosis_core.py
"""
从demo.py复制并改造的核心诊断功能，可以调用而不是print
"""
import textwrap
import time
import asyncio
from typing import Any, List, Optional, Dict, AsyncGenerator

from langchain_core.tools import tool
from langchain_core.language_models.llms import LLM
import re


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
# MockLLM（从demo复制，改为可调用）
# ===============================
class MockLLM(LLM):
    """模拟的大模型，固定输出，确保可离线运行"""

    responses: List[str] = [
        "Action: get_build_log\nAction Input: _",
        "Action: get_k8s_log\nAction Input: _",
        "Action: knowledge_lookup\nAction Input: 这是Pod健康检查失败的日志",
        "Final Answer: 问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
    ]

    index: int = 0
    verbose: bool = True

    @property
    def _llm_type(self) -> str:
        return "mock-llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if self.verbose:
            print(f"\n--- Mock LLM收到Prompt ---")
            print(prompt)
            print("--- End Prompt ---\n")

        if self.index < len(self.responses):
            resp = self.responses[self.index]
            self.index += 1
            return resp
        else:
            return "Final Answer: 没有更多响应"

    def reset(self):
        """重置LLM状态"""
        self.index = 0


# ===============================
# 可调用的诊断服务（从demo改造）
# ===============================
class DiagnosisService:
    """可调用的故障诊断服务"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.tools = {tool.name: tool for tool in [get_build_log, get_k8s_log, get_service_log, knowledge_lookup]}
        self.max_iterations = 10

    def _parse_action(self, response: str) -> Dict[str, str]:
        """解析LLM响应中的Action和Action Input"""
        action_match = re.search(r'Action:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
        input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
        final_match = re.search(r'Final Answer:\s*(.+)', response, re.IGNORECASE | re.DOTALL)

        if final_match:
            return {"type": "final", "content": final_match.group(1).strip()}
        elif action_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            return {"type": "action", "action": action, "input": action_input}
        else:
            return {"type": "thought", "content": response}

    def _get_prompt(self, user_input: str, scratchpad: str) -> str:
        """获取提示词"""
        prompt_template = textwrap.dedent("""\
            你是一个发布流水线故障诊断AI。
            根据用户问题，调用可用工具，逐步分析原因。
            使用以下格式：
            Thought: 你的想法
            Action: 工具名
            Action Input: 工具输入

            当你得出结论时，必须用 Final Answer 格式：
            Final Answer: 你的最终回答

            用户问题: {user_input}

            {scratchpad}Thought:""")
        return prompt_template.format(user_input=user_input, scratchpad=scratchpad)

    async def diagnose_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """流式执行诊断，返回每一步的输出"""
        llm = MockLLM()
        llm.verbose = self.verbose
        scratchpad = ""

        # 发送开始信号
        yield {"type": "start", "message": "开始故障分析..."}

        for iteration in range(self.max_iterations):
            # 构建提示词
            current_prompt = self._get_prompt(user_input, scratchpad)

            # 发送思考状态
            yield {"type": "thinking", "iteration": iteration + 1, "content": "正在分析..."}

            # 获取LLM响应
            llm_response = llm._call(current_prompt)

            # 发送LLM响应
            yield {"type": "llm_response", "content": llm_response}

            # 解析响应
            parsed = self._parse_action(llm_response)

            if parsed["type"] == "final":
                # 发送最终答案
                yield {
                    "type": "final",
                    "content": parsed['content'],
                    "status": "completed"
                }
                return

            elif parsed["type"] == "action":
                action = parsed["action"]
                action_input = parsed["input"]

                # 发送执行工具状态
                yield {"type": "tool_call", "tool": action, "input": action_input}

                # 执行工具
                if action in self.tools:
                    try:
                        tool = self.tools[action]

                        # 为特定工具提供参数
                        if action in ["get_build_log", "get_k8s_log", "get_service_log"]:
                            result = tool.invoke("_")
                        else:
                            result = tool.invoke(action_input)

                        scratchpad += f"Thought: {llm_response}\nAction: {action}\nAction Input: {action_input}\nObservation: {result}\n\n"

                        # 发送工具执行结果
                        yield {"type": "tool_result", "tool": action, "result": result}

                    except Exception as e:
                        result = f"工具执行错误: {e}"
                        scratchpad += f"Thought: {llm_response}\nAction: {action}\nAction Input: {action_input}\nObservation: {result}\n\n"
                        yield {"type": "error", "message": result}
                else:
                    result = f"未知工具: {action}"
                    scratchpad += f"Thought: {llm_response}\nAction: {action}\nAction Input: {action_input}\nObservation: {result}\n\n"
                    yield {"type": "error", "message": result}

            else:
                scratchpad += f"Thought: {parsed['content']}\n"

        # 达到最大迭代次数
        yield {
            "type": "error",
            "message": "达到最大迭代次数，未能得出结论。",
            "status": "failed"
        }

    async def diagnose(self, user_input: str) -> str:
        """同步执行诊断，返回最终结果"""
        final_result = ""
        async for chunk in self.diagnose_stream(user_input):
            if chunk.get("type") == "final":
                final_result = chunk.get("content", "")
                break
        return final_result