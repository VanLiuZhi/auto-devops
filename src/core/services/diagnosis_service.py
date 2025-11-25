"""
诊断服务：使用新架构的故障诊断服务
保持与原有FastAPI接口的兼容性
"""
import json
from typing import Any, AsyncGenerator, Dict

from ..agents.diagnosis_agent import DiagnosisAgent, create_mock_diagnosis_agent, create_glm_diagnosis_agent
from ..configs.scenarios import get_scenario, ALL_SCENARIOS
from ..configs.agent_configs import get_config


class DiagnosisService:
    """
    诊断服务
    使用新的分层架构实现，支持模型切换和场景配置
    保持与原有API的兼容性
    """

    def __init__(self, verbose: bool = False, model_type: str = "mock", scenario_name: str = None):
        """
        初始化诊断服务

        Args:
            verbose: 是否输出详细日志
            model_type: 模型类型 ("mock", "glm", "scenario_based_mock")
            scenario_name: 场景名称（用于Mock模型）
        """
        self.verbose = verbose
        self.model_type = model_type
        self.current_agent = None
        self.current_scenario = None

        # 根据参数创建Agent
        self._create_agent(scenario_name)

    def _create_agent(self, scenario_name: str = None):
        """
        根据当前配置创建Agent实例

        Args:
            scenario_name: 场景名称
        """
        try:
            if self.model_type == "mock":
                # 使用默认Mock模型
                self.current_agent = create_mock_diagnosis_agent(
                    scenario_name=scenario_name or "default",
                    verbose=self.verbose
                )

            elif self.model_type == "scenario_based_mock":
                # 使用基于场景的Mock模型
                self.current_agent = create_mock_diagnosis_agent(
                    scenario_name=scenario_name or "k8s_health_check_failure",
                    verbose=self.verbose
                )

            elif self.model_type == "glm":
                # 使用GLM模型
                self.current_agent = create_glm_diagnosis_agent(verbose=self.verbose)

            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")

            # 如果指定了场景，配置场景
            if scenario_name and scenario_name in ALL_SCENARIOS:
                self.configure_scenario(scenario_name)

        except Exception as e:
            # 创建失败时使用默认Mock模型
            print(f"创建Agent失败，使用默认Mock模型: {str(e)}")
            self.current_agent = create_mock_diagnosis_agent(verbose=self.verbose)

    def configure_scenario(self, scenario_name: str):
        """
        配置诊断场景

        Args:
            scenario_name: 场景名称
        """
        scenario_config = get_scenario(scenario_name)
        if scenario_config:
            self.current_agent.configure_scenario(scenario_config)
            self.current_scenario = scenario_name
        else:
            print(f"场景 '{scenario_name}' 不存在")

    def clear_scenario(self):
        """清除当前场景配置"""
        if self.current_agent:
            self.current_agent.clear_scenario()
        self.current_scenario = None

    def switch_model(self, model_type: str, scenario_name: str = None):
        """
        切换模型类型

        Args:
            model_type: 新的模型类型
            scenario_name: 场景名称（可选）
        """
        # 清理当前Agent
        if self.current_agent:
            self.current_agent.reset()

        # 更新模型类型
        self.model_type = model_type

        # 创建新的Agent
        self._create_agent(scenario_name)

    def reset(self):
        """重置服务状态"""
        if self.current_agent:
            self.current_agent.reset()

    async def diagnose_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式执行诊断，返回每一步的输出
        保持与原有接口的兼容性

        Args:
            user_input: 用户输入

        Yields:
            每个步骤的结果字典
        """
        if not self.current_agent:
            yield {
                "type": "error",
                "message": "诊断Agent未初始化",
                "status": "failed"
            }
            return

        try:
            # 转换Agent输出为原有格式
            async for chunk in self.current_agent.diagnose_stream(user_input):
                # 保持与原有接口格式的兼容性
                if chunk["type"] == "start":
                    yield {
                        "type": "start",
                        "message": chunk.get("message", "开始故障分析...")
                    }

                elif chunk["type"] == "thinking":
                    # 可以选择性地输出思考过程
                    if self.verbose:
                        yield {
                            "type": "thinking",
                            "iteration": chunk.get("iteration", 0),
                            "content": chunk.get("message", "正在分析...")
                        }

                elif chunk["type"] == "tool_call":
                    yield {
                        "type": "tool_call",
                        "tool": chunk.get("tool", ""),
                        "input": chunk.get("input", {})
                    }

                elif chunk["type"] == "tool_result":
                    yield {
                        "type": "tool_result",
                        "tool": chunk.get("tool", ""),
                        "result": chunk.get("result", "")
                    }

                elif chunk["type"] == "final":
                    yield {
                        "type": "final",
                        "content": chunk.get("content", ""),
                        "status": "completed"
                    }

                elif chunk["type"] == "error":
                    yield {
                        "type": "error",
                        "message": chunk.get("message", "诊断过程中出现错误"),
                        "status": "failed"
                    }

        except Exception as e:
            yield {
                "type": "error",
                "message": f"诊断过程中出现错误: {str(e)}",
                "status": "failed"
            }

    async def diagnose(self, user_input: str) -> str:
        """
        同步执行诊断，返回最终结果
        保持与原有接口的兼容性

        Args:
            user_input: 用户输入

        Returns:
            诊断结果字符串
        """
        if not self.current_agent:
            return "诊断Agent未初始化"

        try:
            result = await self.current_agent.diagnose(user_input)

            if result.get("success"):
                return result.get("final_answer", "未能获得诊断结果")
            else:
                return result.get("error", "诊断失败")

        except Exception as e:
            return f"诊断执行失败: {str(e)}"

    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息

        Returns:
            服务配置信息
        """
        info = {
            "model_type": self.model_type,
            "verbose": self.verbose,
            "current_scenario": self.current_scenario
        }

        if self.current_agent:
            agent_info = self.current_agent.get_agent_info()
            info.update(agent_info)

        return info

    async def test_scenario(self, scenario_name: str, user_input: str = "发布任务失败，请分析原因") -> Dict[str, Any]:
        """
        测试指定场景

        Args:
            scenario_name: 场景名称
            user_input: 测试输入

        Returns:
            测试结果
        """
        # 保存当前状态
        original_scenario = self.current_scenario

        try:
            # 配置测试场景
            self.configure_scenario(scenario_name)

            # 执行诊断
            steps = []
            async for chunk in self.diagnose_stream(user_input):
                steps.append(chunk)

                # 如果是最终结果，跳出循环
                if chunk.get("type") == "final":
                    break

            # 获取最终结果
            final_result = await self.diagnose(user_input)

            return {
                "scenario": scenario_name,
                "success": True,
                "steps": steps,
                "final_result": final_result,
                "total_steps": len(steps)
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "success": False,
                "error": str(e),
                "steps": [],
                "final_result": None
            }

        finally:
            # 恢复原始场景
            if original_scenario:
                self.configure_scenario(original_scenario)
            else:
                self.clear_scenario()


# 便捷创建函数
def create_diagnosis_service(
    model_type: str = "scenario_based_mock",
    scenario_name: str = "k8s_health_check_failure",
    verbose: bool = False
) -> DiagnosisService:
    """
    创建诊断服务的便捷函数

    Args:
        model_type: 模型类型
        scenario_name: 场景名称
        verbose: 是否输出详细日志

    Returns:
        诊断服务实例
    """
    return DiagnosisService(
        verbose=verbose,
        model_type=model_type,
        scenario_name=scenario_name
    )