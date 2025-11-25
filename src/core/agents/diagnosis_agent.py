"""
诊断Agent：高级Agent接口，整合ReAct执行器和配置管理
"""
from typing import Dict, Any, AsyncGenerator

from ..models.base_llm import BaseLLM
from ..models.model_factory import ModelFactory, ModelType
from ..tools.tool_manager import ToolManager
from .react_executor import ReActExecutor


class DiagnosisAgent:
    """
    诊断Agent
    提供高级的诊断接口，整合模型、工具和ReAct执行器
    """

    def __init__(
        self,
        model_config: Dict[str, Any],
        verbose: bool = False,
        max_iterations: int = 10
    ):
        """
        初始化诊断Agent

        Args:
            model_config: 模型配置字典
            verbose: 是否输出详细日志
            max_iterations: 最大迭代次数
        """
        self.verbose = verbose
        self.max_iterations = max_iterations

        # 创建LLM实例
        self.llm = ModelFactory.create_from_config(model_config)

        # 创建工具管理器
        self.tool_manager = ToolManager()

        # 创建ReAct执行器
        self.executor = ReActExecutor(
            llm=self.llm,
            tool_manager=self.tool_manager,
            max_iterations=max_iterations,
            verbose=verbose
        )

        # 场景配置
        self.current_scenario = None

    def configure_scenario(self, scenario_config: Dict[str, Any]):
        """
        配置诊断场景

        Args:
            scenario_config: 场景配置，包含模型和工具配置
        """
        self.current_scenario = scenario_config

        # 配置LLM场景
        if "model" in scenario_config:
            model_scenario = scenario_config["model"]
            if hasattr(self.llm, 'set_scenario_config'):
                self.llm.set_scenario_config(model_scenario)

        # 配置工具场景
        if "tools" in scenario_config:
            from ..tools.diagnosis_tools import set_tool_scenario
            set_tool_scenario(scenario_config["tools"])

    def clear_scenario(self):
        """清除场景配置"""
        self.current_scenario = None

        # 清除LLM场景
        if hasattr(self.llm, 'set_scenario_config'):
            self.llm.set_scenario_config(None)

        # 清除工具场景
        from ..tools.diagnosis_tools import clear_tool_scenario
        clear_tool_scenario()

    def reset(self):
        """重置Agent状态"""
        self.llm.reset()
        self.clear_scenario()

    async def diagnose(self, user_input: str) -> Dict[str, Any]:
        """
        执行诊断（同步模式）

        Args:
            user_input: 用户输入的问题

        Returns:
            诊断结果字典
        """
        try:
            result = await self.executor.invoke(user_input)

            # 添加额外的元数据
            result["agent_info"] = {
                "model_type": self.llm._llm_type,
                "scenario": self.current_scenario.get("name") if self.current_scenario else None,
                "total_tools": len(self.tool_manager.get_tool_names())
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"诊断执行失败: {str(e)}",
                "agent_info": {
                    "model_type": self.llm._llm_type,
                    "scenario": self.current_scenario.get("name") if self.current_scenario else None
                }
            }

    async def diagnose_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        执行诊断（流式模式）

        Args:
            user_input: 用户输入的问题

        Yields:
            每个步骤的结果
        """
        try:
            async for chunk in self.executor.stream(user_input):
                # 添加Agent信息到最终结果
                if chunk.get("type") in ["final", "error"]:
                    chunk["agent_info"] = {
                        "model_type": self.llm._llm_type,
                        "scenario": self.current_scenario.get("name") if self.current_scenario else None,
                        "total_tools": len(self.tool_manager.get_tool_names())
                    }

                yield chunk

        except Exception as e:
            yield {
                "type": "error",
                "message": f"诊断执行失败: {str(e)}",
                "agent_info": {
                    "model_type": self.llm._llm_type,
                    "scenario": self.current_scenario.get("name") if self.current_scenario else None
                }
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取Agent信息

        Returns:
            Agent配置信息
        """
        return {
            "model_type": self.llm._llm_type,
            "max_iterations": self.max_iterations,
            "verbose": self.verbose,
            "available_tools": self.tool_manager.get_tool_names(),
            "current_scenario": self.current_scenario.get("name") if self.current_scenario else None,
            "total_tools": len(self.tool_manager.get_tool_names())
        }


class DiagnosisAgentBuilder:
    """
    诊断Agent构建器
    提供流式API来构建和配置诊断Agent
    """

    def __init__(self):
        self.model_config = {"type": "mock", "params": {}}
        self.verbose = False
        self.max_iterations = 10
        self.scenario_config = None

    def with_mock_model(self, scenario_name: str = "default", **kwargs):
        """使用Mock模型"""
        self.model_config = {
            "type": "mock",
            "params": {"scenario_name": scenario_name, **kwargs}
        }
        return self

    def with_scenario_mock_model(self, scenario_name: str = "k8s_health_check_failure", **kwargs):
        """使用基于场景的Mock模型"""
        self.model_config = {
            "type": "scenario_based_mock",
            "params": {"scenario_name": scenario_name, **kwargs}
        }
        return self

    def with_glm_model(self, api_key: str = None, **kwargs):
        """使用GLM模型"""
        self.model_config = {
            "type": "glm",
            "params": {"api_key": api_key, **kwargs}
        }
        return self

    def with_verbose(self, verbose: bool = True):
        """设置详细日志"""
        self.verbose = verbose
        return self

    def with_max_iterations(self, max_iterations: int):
        """设置最大迭代次数"""
        self.max_iterations = max_iterations
        return self

    def with_scenario(self, scenario_config: Dict[str, Any]):
        """设置场景配置"""
        self.scenario_config = scenario_config
        return self

    def build(self) -> DiagnosisAgent:
        """构建诊断Agent"""
        agent = DiagnosisAgent(
            model_config=self.model_config,
            verbose=self.verbose,
            max_iterations=self.max_iterations
        )

        if self.scenario_config:
            agent.configure_scenario(self.scenario_config)

        return agent


# 便捷创建函数
def create_mock_diagnosis_agent(
    scenario_name: str = "k8s_health_check_failure",
    verbose: bool = False
) -> DiagnosisAgent:
    """
    创建Mock诊断Agent的便捷函数

    Args:
        scenario_name: 场景名称
        verbose: 是否输出详细日志

    Returns:
        诊断Agent实例
    """
    return (DiagnosisAgentBuilder()
            .with_scenario_mock_model(scenario_name)
            .with_verbose(verbose)
            .build())


def create_glm_diagnosis_agent(
    api_key: str = None,
    verbose: bool = False
) -> DiagnosisAgent:
    """
    创建GLM诊断Agent的便捷函数

    Args:
        api_key: GLM API密钥
        verbose: 是否输出详细日志

    Returns:
        诊断Agent实例
    """
    return (DiagnosisAgentBuilder()
            .with_glm_model(api_key)
            .with_verbose(verbose)
            .build())