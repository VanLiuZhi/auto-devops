# demo_agent_mock.py
import textwrap

from langchain_core.tools import tool
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from typing import Any, List, Optional, Dict
import re
import time


# ===============================
# 延迟打印工具
# ===============================
def delayed_print(content: str, delay: float = 1.0):
    """延迟打印工具，模拟真实的调用延迟

    Args:
        content: 要打印的内容
        delay: 延迟时间（秒），默认1秒
    """
    time.sleep(delay)
    print(content)


# ===============================
# 模拟知识库
# TODO 这个模拟太简单了，实际应该要结合词嵌入模型和向量查询。最好是能让AI直接阅读markdown文档处理，没必要使用词嵌入模型
# ===============================
knowledge_base = {
    "健康检查失败": "请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
}


# ===============================
# 定义工具
# ===============================
@tool
def get_build_log(input_str: str = "") -> str:
    """获取编译构建阶段的日志"""
    return "[编译阶段日志] Maven 编译成功，没有错误。"


@tool
def get_k8s_log(input_str: str = "") -> str:
    """获取K8s部署阶段的日志"""
    return "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。"


@tool
def get_service_log(input_str: str = "") -> str:
    """获取服务启动阶段的日志"""
    return "[服务启动日志] 服务正常启动。"


@tool
def knowledge_lookup(query: str) -> str:
    """从知识库中查找对应的解决方案"""
    for key, solution in knowledge_base.items():
        if key in query:
            return solution
    return ""


# ===============================
# 自定义 Mock LLM
# ===============================
class MockLLM(LLM):
    """一个模拟的大模型，固定输出，确保可离线运行"""

    # 模拟 Agent 与模型交互的多轮响应
    responses: List[str] = [
        # 1. 第一次思考：决定调用 get_build_log
        "Action: get_build_log\nAction Input: _",
        # 2. 接收到build日志后 -> 决定调用 get_k8s_log
        "Action: get_k8s_log\nAction Input: _",
        # 3. 接收到k8s日志后 -> 决定调用 knowledge_lookup
        "Action: knowledge_lookup\nAction Input: 这是Pod健康检查失败的日志",
        # 4. 输出最终答案
        "Final Answer: 问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
    ]

    index: int = 0

    @property
    def _llm_type(self) -> str:
        return "mock-llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # 打印prompt方便调试
        delayed_print("\n--- Mock LLM收到Prompt ---", 0.5)
        delayed_print(prompt, 0.8)
        delayed_print("--- End Prompt ---\n", 0.5)

        if self.index < len(self.responses):
            resp = self.responses[self.index]
            self.index += 1
            return resp
        else:
            return "Action: Final Answer\nAction Input: 没有更多响应"


# ===============================
# 简化的Agent执行器
# ===============================
PROMPT_TEMPLATE = textwrap.dedent("""\
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


def get_prompt(user_input, scratchpad):
    # 先 dedent，再 format
    return PROMPT_TEMPLATE.format(user_input=user_input, scratchpad=scratchpad)


class SimpleAgentExecutor:
    """简化的Agent执行器，支持ReAct模式"""

    def __init__(self, tools: List, llm: LLM, verbose: bool = False):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm
        self.verbose = verbose
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

    def invoke(self, input_data: Dict) -> Dict:
        """执行Agent推理"""
        user_input = input_data["input"]
        scratchpad = ""

        if self.verbose:
            delayed_print(f"\n=== 用户输入 ===\n{user_input}", 1.0)

        for iteration in range(self.max_iterations):
            # 　构建提示词
            current_prompt = get_prompt(user_input, scratchpad)

            # 获取LLM响应
            llm_response = self.llm._call(current_prompt)

            if self.verbose:
                delayed_print(f"\n=== LLM响应 ===\n{llm_response}", 1.2)

            # 解析响应
            parsed = self._parse_action(llm_response)

            if parsed["type"] == "final":
                if self.verbose:
                    delayed_print(f"\n=== 最终答案 ===\n{parsed['content']}", 1.5)
                return {"output": parsed['content']}

            elif parsed["type"] == "action":
                action = parsed["action"]
                action_input = parsed["input"]

                if self.verbose:
                    delayed_print(f"\n=== 执行工具 ===\n{action}: {action_input}", 0.8)

                # 执行工具
                if action in self.tools:
                    try:
                        tool = self.tools[action]
                        # 为特定工具提供参数
                        if action in ["get_build_log", "get_k8s_log", "get_service_log"]:
                            result = tool.invoke("_")  # 总是传递下划线参数
                        else:
                            result = tool.invoke(action_input)

                        scratchpad += f"Thought: {llm_response}\nAction: {action}\nAction Input: {action_input}\nObservation: {result}\n\n"

                        if self.verbose:
                            delayed_print(f"工具结果: {result}", 1.0)
                    except Exception as e:
                        result = f"工具执行错误: {e}"
                        scratchpad += f"Thought: {llm_response}\nAction: {action}\nAction Input: {action_input}\nObservation: {result}\n\n"
                else:
                    result = f"未知工具: {action}"
                    scratchpad += f"Thought: {llm_response}\nAction: {action}\nAction Input: {action_input}\nObservation: {result}\n\n"

            else:
                scratchpad += f"Thought: {parsed['content']}\n"

            # if iteration < 3:
            #     print(f"\n===总结 当前迭代为 {iteration}")
            #     delayed_print(f"\n=== 当前迭代为 {iteration}，下次思考过程 ===\n{scratchpad}", 2)
            #     print(f"\n===总结结束 当前迭代为 {iteration}")

        return {"output": "达到最大迭代次数，未能得出结论。"}


# 初始化
tools = [get_build_log, get_k8s_log, get_service_log, knowledge_lookup]
llm = MockLLM()
agent_executor = SimpleAgentExecutor(tools=tools, llm=llm, verbose=True)


# ===============================
# 运行 Demo
# ===============================
def run_demo():
    delayed_print("\n=== 开始故障分析（Mock LLM模式） ===\n", 1.5)
    result = agent_executor.invoke({"input": "发布任务失败，请分析原因"})
    delayed_print("\n=== 最终分析结果 ===", 1.2)
    delayed_print(result["output"], 1.0)


if __name__ == "__main__":
    run_demo()
