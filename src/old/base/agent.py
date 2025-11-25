# demo_agent_mock_v2.py
import textwrap
import json
import requests

from langchain_core.tools import tool
from langchain_core.language_models.llms import LLM
from typing import Any, List, Optional, Dict
import re
import time


# ===============================
# 延迟打印工具
# ===============================
def delayed_print(content: str, delay: float = 0.5):
    """延迟打印工具"""
    time.sleep(delay)
    print(content, flush=True)


# ===============================
# 模拟知识库
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
# GLM-4.6 LLM 实现
# ===============================
class GLMLLM(LLM):
    """使用智谱GLM-4.6大模型的LLM实现"""

    # api_key: str = "4b42d63c64aa4cd1a23b0ae0b5ba8a57.R4gzQuQlqJ51HA25"
    api_key: str = "xxx."
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    model: str = "glm-4.6"

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(**kwargs)
        if api_key:
            self.api_key = api_key

    @property
    def _llm_type(self) -> str:
        return "glm-4-6"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        messages = [
            {
                "role": "system",
                "content": "你是专业的发布流水线故障诊断AI助手。请严格按照用户提供的流程和工具要求执行，每次只能调用一个工具。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "stream": False
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            )
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content
            else:
                return "Final Answer: API返回格式错误"
        except Exception as e:
            return f"Final Answer: API调用失败: {str(e)}"


# ===============================
# 简化的Agent执行器（双模式日志）
# ===============================
PROMPT_TEMPLATE = textwrap.dedent("""\
    你是一个专业的发布流水线故障诊断AI助手。

    【工作目标】
    你严格按照以下顺序执行诊断流程：
    1. 获取并分析编译日志（工具：get_build_log）
    2. 获取并分析 Kubernetes 部署日志（工具：get_k8s_log）
    3. 获取并分析服务启动日志（工具：get_service_log）

    【执行规则】
    - 每次只调用一个工具
    - 调用工具后必须等待结果再分析
    - 日志分析时必须提炼关键错误信息
    - 如果某一步发现明确错误，立即调用 knowledge_lookup 查询解决方案
    - 所有结论必须基于工具返回的真实数据
    - 按照 1→2→3 顺序执行

    【可用工具】：
    - get_build_log
    - get_k8s_log
    - get_service_log
    - knowledge_lookup

    【循环执行逻辑】：
    1. 当前步骤 = 1
    2. 调用工具获取日志
    3. 分析日志：
        - 有错误 → 保存原因 → 查询知识库 → 输出 Final Answer
        - 无错误 → 步骤号+1 → <=3 则继续，否则 Final Answer

    【输出格式】：
    Thought: （分析思路）
    Action: （工具名）
    Action Input: （工具参数）

    【最终答复】：
    Final Answer: （最终结论）

    【用户问题】：
    {user_input}

    {scratchpad}
    Thought:
    """)


def get_prompt(user_input, scratchpad):
    return PROMPT_TEMPLATE.format(user_input=user_input, scratchpad=scratchpad)


class SimpleAgentExecutor:
    """简化的Agent执行器，双模式日志"""

    def __init__(self, tools: List, llm: LLM, log_mode: str = "normal", max_iterations: int = 10):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm
        self.log_mode = log_mode  # normal / debug
        self.max_iterations = max_iterations

    def _parse_action(self, response: str) -> Dict[str, str]:
        action_match = re.search(r'Action:\s*(.+?)(?=\n|$)', response)
        input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', response)
        final_match = re.search(r'Final Answer:\s*(.+)', response, re.DOTALL)
        if final_match:
            return {"type": "final", "content": final_match.group(1).strip()}
        elif action_match:
            return {"type": "action", "action": action_match.group(1).strip(),
                    "input": input_match.group(1).strip() if input_match else ""}
        else:
            return {"type": "thought", "content": response}

    def invoke(self, input_data: Dict) -> Dict:
        user_input = input_data["input"]
        scratchpad = ""

        if self.log_mode == "debug":
            delayed_print(f"\n[DEBUG] 用户输入: {user_input}")

        for iteration in range(self.max_iterations):
            current_prompt = get_prompt(user_input, scratchpad)

            if self.log_mode == "debug":
                delayed_print(f"\n[DEBUG] Prompt:\n{current_prompt}")

            llm_response = self.llm._call(current_prompt)

            if self.log_mode == "debug":
                delayed_print(f"\n[DEBUG] LLM响应:\n{llm_response}")

            parsed = self._parse_action(llm_response)

            if parsed["type"] == "final":
                if self.log_mode == "normal":
                    print(f"✅ Final Answer → {parsed['content']}")
                else:
                    delayed_print(f"\n[DEBUG] 最终答案:\n{parsed['content']}")
                return {"output": parsed['content']}

            elif parsed["type"] == "action":
                action = parsed["action"]
                action_input = parsed["input"]

                if self.log_mode == "normal":
                    print(f"Step {iteration + 1} → 调用 {action} → 参数: {action_input}")

                if action in self.tools:
                    try:
                        result = self.tools[action].invoke(action_input if action not in
                                                                           ["get_build_log", "get_k8s_log",
                                                                            "get_service_log"]
                                                           else "_")
                        scratchpad += f"Observation: {result}\n\n"
                        if self.log_mode == "normal":
                            print(f"    结果: {result}")
                        elif self.log_mode == "debug":
                            delayed_print(f"[DEBUG] 工具结果: {result}")
                    except Exception as e:
                        scratchpad += f"Observation: 工具执行错误: {e}\n\n"
                else:
                    scratchpad += f"Observation: 未知工具 {action}\n\n"

            else:
                scratchpad += f"Thought: {parsed['content']}\n"

        return {"output": "达到最大迭代次数，未能得出结论。"}


# 初始化
tools = [get_build_log, get_k8s_log, get_service_log, knowledge_lookup]
llm = GLMLLM()
agent_executor = SimpleAgentExecutor(tools=tools, llm=llm, log_mode="normal")  # normal / debug


def run_demo():
    delayed_print("\n=== 开始故障分析（GLM-4.6模式） ===", 1.0)
    result = agent_executor.invoke({"input": "发布任务失败，请分析原因"})
    delayed_print("\n=== 最终分析结果 ===", 0.5)
    delayed_print(result["output"], 0.5)


if __name__ == "__main__":
    run_demo()