"""
增强的MockLLM实现，支持基于场景配置的动态响应
"""
from typing import List, Optional, Dict, Any
import random

from .base_llm import BaseLLM


class MockLLM(BaseLLM):
    """
    增强的MockLLM，支持基于场景配置的动态响应
    可以通过场景配置来模拟不同的诊断流程
    """

    def __init__(self, verbose: bool = False, scenario_name: str = "default"):
        super().__init__(verbose)
        self.scenario_name = scenario_name
        self.call_count = 0  # 记录调用次数，用于返回不同的响应

    @property
    def _llm_type(self) -> str:
        return "mock-llm"

    def reset(self):
        """重置MockLLM状态"""
        super().reset()
        self.call_count = 0

    def _get_response_for_scenario(self) -> str:
        """
        根据场景配置和调用次数返回响应
        场景配置格式：
        {
            "sequence": [
                {"type": "thought", "content": "..."},
                {"type": "action", "tool": "tool_name", "input": "..."},
                {"type": "final", "content": "..."}
            ],
            "randomize": False  # 是否随机化响应
        }
        """
        if not self._scenario_config:
            # 默认场景：标准的诊断流程
            return self._get_default_response()

        sequence = self._scenario_config.get("sequence", [])
        if not sequence:
            return self._get_default_response()

        if self.call_count < len(sequence):
            current_step = sequence[self.call_count]
            step_type = current_step.get("type", "thought")

            if step_type == "action":
                tool = current_step.get("tool", "")
                input_str = current_step.get("input", "")
                return f"Action: {tool}\nAction Input: {input_str}"
            elif step_type == "thought":
                return current_step.get("content", "")
            elif step_type == "final":
                return f"Final Answer: {current_step.get('content', '')}"

        return "Final Answer: 流程已结束"

    def _get_default_response(self) -> str:
        """默认的诊断流程响应"""
        default_sequence = [
            "我需要分析发布任务失败的原因。让我先获取编译构建日志。",
            "Action: get_build_log\nAction Input: _",
            "编译构建成功了，现在让我检查K8s部署日志。",
            "Action: get_k8s_log\nAction Input: _",
            "发现Pod健康检查失败，让我获取服务启动日志进一步确认。",
            "Action: get_service_log\nAction Input: _",
            "根据日志分析，这是Pod健康检查失败的问题。让我查询知识库获取解决方案。",
            "Action: knowledge_lookup\nAction Input: Pod健康检查失败",
            "Final Answer: 问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
        ]

        if self.call_count < len(default_sequence):
            return default_sequence[self.call_count]

        return "Final Answer: 诊断流程已结束"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """生成Mock响应"""
        response = self._get_response_for_scenario()
        self.call_count += 1
        return response


class ScenarioBasedMockLLM(MockLLM):
    """
    基于特定场景的MockLLM
    """

    def __init__(self, scenario_config: Dict[str, Any], verbose: bool = False):
        super().__init__(verbose, scenario_name=scenario_config.get("name", "custom"))
        self.set_scenario_config(scenario_config)


# 预定义的场景配置
PREDEFINED_SCENARIOS = {
    "k8s_health_check_failure": {
        "name": "k8s_health_check_failure",
        "description": "K8s健康检查失败场景",
        "sequence": [
            {"type": "thought", "content": "发布任务失败了，让我先检查编译构建日志。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译没问题，现在检查K8s部署日志。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "发现了问题！Pod健康检查失败，端口8080无法访问。让我检查服务日志确认。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "服务确实启动了，但健康检查配置有问题。查询知识库。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "健康检查失败"},
            {"type": "final", "content": "问题阶段：K8s部署Pod\n原因分析：Pod健康检查失败，端口8080无法访问\n解决方案：请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"}
        ]
    },

    "compilation_failure": {
        "name": "compilation_failure",
        "description": "编译失败场景",
        "sequence": [
            {"type": "thought", "content": "发布任务失败，让我先检查编译构建日志。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "发现了编译错误！Maven构建失败，依赖项缺失。让我查询解决方案。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "编译失败"},
            {"type": "final", "content": "问题阶段：编译构建\n原因分析：Maven编译失败，依赖项缺失或版本冲突\n解决方案：请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。"}
        ]
    },

    "runtime_failure": {
        "name": "runtime_failure",
        "description": "运行时错误场景",
        "sequence": [
            {"type": "thought", "content": "发布任务失败，让我按步骤检查。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译正常，检查K8s部署。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "部署也成功了，检查服务启动日志。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "发现了运行时错误！服务启动后出现NullPointerException。查询解决方案。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "运行时错误"},
            {"type": "final", "content": "问题阶段：服务运行\n原因分析：服务启动后出现NullPointerException，可能是配置缺失或空引用\n解决方案：请检查服务启动日志中的详细错误堆栈，确认相关配置文件是否存在且格式正确，检查代码中的空值处理逻辑。"}
        ]
    }
}


def create_mock_llm(scenario_name: str, verbose: bool = False) -> MockLLM:
    """
    创建基于预定义场景的MockLLM

    Args:
        scenario_name: 场景名称
        verbose: 是否输出详细日志

    Returns:
        MockLLM实例
    """
    if scenario_name in PREDEFINED_SCENARIOS:
        return ScenarioBasedMockLLM(PREDEFINED_SCENARIOS[scenario_name], verbose)
    else:
        return MockLLM(verbose, scenario_name)