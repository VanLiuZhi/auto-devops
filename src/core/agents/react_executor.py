"""
ReAct执行器：实现完整的ReAct（Reasoning + Acting）流程
"""
import textwrap
import asyncio
from typing import Any, List, Optional, Dict, AsyncGenerator, Tuple
import re

from ..models.base_llm import BaseLLM
from ..tools.tool_manager import ToolManager


class ReActExecutor:
    """
    ReAct执行器
    实现完整的思考-行动循环流程
    """

    def __init__(
        self,
        llm: BaseLLM,
        tool_manager: ToolManager,
        max_iterations: int = 10,
        verbose: bool = False
    ):
        self.llm = llm
        self.tool_manager = tool_manager
        self.max_iterations = max_iterations
        self.verbose = verbose

        # ReAct提示词模板
        self.prompt_template = textwrap.dedent("""\
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
            {tools_description}

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

    def _get_tools_description(self) -> str:
        """获取工具描述"""
        descriptions = self.tool_manager.get_tool_descriptions()
        tool_desc_lines = []
        for name, desc in descriptions.items():
            tool_desc_lines.append(f"- {name}: {desc}")
        return "\n".join(tool_desc_lines)

    def _get_prompt(self, user_input: str, scratchpad: str) -> str:
        """生成完整的提示词"""
        tools_description = self._get_tools_description()
        return self.prompt_template.format(
            tools_description=tools_description,
            user_input=user_input,
            scratchpad=scratchpad
        )

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应，提取行动信息

        Returns:
            解析结果字典，包含type字段：
            - "final": 最终答案
            - "action": 工具调用
            - "thought": 思考过程
        """
        # 尝试匹配最终答案
        final_match = re.search(r'Final Answer:\s*(.+)', response, re.DOTALL | re.IGNORECASE)
        if final_match:
            return {
                "type": "final",
                "content": final_match.group(1).strip()
            }

        # 尝试匹配工具调用
        action_match = re.search(r'Action:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
        input_match = re.search(r'Action Input:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)

        if action_match:
            action = action_match.group(1).strip()
            action_input = input_match.group(1).strip() if input_match else ""
            return {
                "type": "action",
                "action": action,
                "input": action_input
            }

        # 默认为思考过程
        return {
            "type": "thought",
            "content": response.strip()
        }

    async def _execute_tool(self, tool_name: str, tool_input: str) -> Tuple[str, bool]:
        """
        执行工具调用

        Args:
            tool_name: 工具名称
            tool_input: 工具输入

        Returns:
            (结果, 是否成功)
        """
        try:
            if not self.tool_manager.has_tool(tool_name):
                return f"错误：未知工具 '{tool_name}'", False

            result = self.tool_manager.invoke_tool(tool_name, tool_input)
            return result, True

        except Exception as e:
            return f"工具执行错误: {str(e)}", False

    async def _execute_step(
        self,
        iteration: int,
        user_input: str,
        scratchpad: str
    ) -> Tuple[Dict[str, Any], str]:
        """
        执行单个ReAct步骤

        Args:
            iteration: 当前迭代次数
            user_input: 用户输入
            scratchpad: 当前记忆板

        Returns:
            (步骤结果, 新的记忆板)
        """
        # 生成提示词
        prompt = self._get_prompt(user_input, scratchpad)

        # 调用LLM
        llm_response = self.llm(prompt)

        # 解析响应
        parsed = self._parse_action(llm_response)

        # 准备步骤结果
        step_result = {
            "iteration": iteration,
            "llm_response": llm_response,
            "parsed_type": parsed["type"]
        }

        new_scratchpad = scratchpad

        if parsed["type"] == "final":
            step_result["final_answer"] = parsed["content"]
            new_scratchpad += f"Final Answer: {parsed['content']}\n"

        elif parsed["type"] == "action":
            action = parsed["action"]
            action_input = parsed["input"]

            step_result["tool_call"] = {
                "tool": action,
                "input": action_input
            }

            # 执行工具
            tool_result, success = await self._execute_tool(action, action_input)

            step_result["tool_result"] = {
                "tool": action,
                "result": tool_result,
                "success": success
            }

            new_scratchpad += f"Thought: {llm_response}\n"
            new_scratchpad += f"Action: {action}\n"
            new_scratchpad += f"Action Input: {action_input}\n"
            new_scratchpad += f"Observation: {tool_result}\n\n"

        elif parsed["type"] == "thought":
            step_result["thought"] = parsed["content"]
            new_scratchpad += f"Thought: {parsed['content']}\n"

        return step_result, new_scratchpad

    async def invoke(self, user_input: str) -> Dict[str, Any]:
        """
        同步执行ReAct流程

        Args:
            user_input: 用户输入

        Returns:
            执行结果字典
        """
        scratchpad = ""
        steps = []

        for iteration in range(self.max_iterations):
            step_result, scratchpad = await self._execute_step(iteration, user_input, scratchpad)
            steps.append(step_result)

            # 如果获得最终答案，结束流程
            if step_result["parsed_type"] == "final":
                return {
                    "success": True,
                    "final_answer": step_result["final_answer"],
                    "steps": steps,
                    "total_iterations": iteration + 1
                }

        # 达到最大迭代次数
        return {
            "success": False,
            "error": "达到最大迭代次数，未能得出结论",
            "steps": steps,
            "total_iterations": self.max_iterations
        }

    async def stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式执行ReAct流程

        Args:
            user_input: 用户输入

        Yields:
            每个步骤的结果
        """
        scratchpad = ""

        # 发送开始信号
        yield {
            "type": "start",
            "message": "开始故障分析...",
            "total_iterations": self.max_iterations
        }

        for iteration in range(self.max_iterations):
            # 发送思考状态
            yield {
                "type": "thinking",
                "iteration": iteration + 1,
                "message": f"正在分析第 {iteration + 1} 步..."
            }

            # 执行步骤
            step_result, scratchpad = await self._execute_step(iteration, user_input, scratchpad)

            # 发送LLM响应
            yield {
                "type": "llm_response",
                "iteration": iteration + 1,
                "content": step_result["llm_response"]
            }

            # 处理不同类型的步骤结果
            if step_result["parsed_type"] == "action":
                # 发送工具调用
                yield {
                    "type": "tool_call",
                    "iteration": iteration + 1,
                    "tool": step_result["tool_call"]["tool"],
                    "input": step_result["tool_call"]["input"]
                }

                # 发送工具结果
                yield {
                    "type": "tool_result",
                    "iteration": iteration + 1,
                    "tool": step_result["tool_result"]["tool"],
                    "result": step_result["tool_result"]["result"],
                    "success": step_result["tool_result"]["success"]
                }

            elif step_result["parsed_type"] == "final":
                # 发送最终答案
                yield {
                    "type": "final",
                    "iteration": iteration + 1,
                    "content": step_result["final_answer"],
                    "status": "completed"
                }
                return

        # 达到最大迭代次数
        yield {
            "type": "error",
            "message": "达到最大迭代次数，未能得出结论",
            "status": "failed"
        }