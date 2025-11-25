# diagnosis_core.py
"""
基于新架构的故障诊断服务 - 保持向后兼容性
使用完整的ReAct流程和动态场景配置
"""
import asyncio
from typing import Any, Dict, AsyncGenerator

# 导入新的核心架构
from ..core.services.diagnosis_service import DiagnosisService as CoreDiagnosisService
from ..core.configs.agent_configs import DEVELOPMENT_CONFIG


class DiagnosisService:
    """
    诊断服务适配器
    保持与原有FastAPI接口的完全兼容性，内部使用新的核心架构
    """

    def __init__(self, verbose: bool = False):
        """
        初始化诊断服务

        Args:
            verbose: 是否输出详细日志
        """
        # 创建核心诊断服务实例
        # 默认使用基于场景的Mock模型，便于测试和演示
        self.core_service = CoreDiagnosisService(
            verbose=verbose,
            model_type="scenario_based_mock",
            scenario_name="k8s_health_check_failure"
        )

    async def diagnose_stream(self, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式执行诊断，返回每一步的输出
        完全兼容原有的接口格式

        Args:
            user_input: 用户输入的问题

        Yields:
            每个步骤的结果字典，格式与原有实现保持一致
        """
        async for chunk in self.core_service.diagnose_stream(user_input):
            yield chunk

    async def diagnose(self, user_input: str) -> str:
        """
        同步执行诊断，返回最终结果
        完全兼容原有的接口格式

        Args:
            user_input: 用户输入的问题

        Returns:
            诊断结果字符串
        """
        return await self.core_service.diagnose(user_input)

    # 新增的便利方法，用于高级配置和测试

    def configure_scenario(self, scenario_name: str):
        """
        配置诊断场景（新功能）

        Args:
            scenario_name: 场景名称
            - "k8s_health_check_failure": K8s健康检查失败
            - "compilation_failure": 编译失败
            - "runtime_failure": 运行时错误
            - "multi_step_complex": 复杂多步骤问题
            - "normal_flow": 正常流程
        """
        self.core_service.configure_scenario(scenario_name)

    def switch_to_real_model(self, api_key: str = None):
        """
        切换到真实GLM模型（新功能）

        Args:
            api_key: GLM API密钥
        """
        self.core_service.switch_model("glm")
        if api_key:
            # 如果提供了API密钥，更新模型配置
            from ..core.models import ModelFactory, ModelType
            new_llm = ModelFactory.create_model(ModelType.GLM, api_key=api_key)
            self.core_service.current_agent.llm = new_llm

    def switch_to_mock_model(self, scenario_name: str = "k8s_health_check_failure"):
        """
        切换到Mock模型（新功能）

        Args:
            scenario_name: 场景名称
        """
        self.core_service.switch_model("scenario_based_mock", scenario_name)

    def get_service_info(self) -> Dict[str, Any]:
        """
        获取当前服务配置信息（新功能）

        Returns:
            服务配置信息字典
        """
        return self.core_service.get_service_info()

    async def test_all_scenarios(self, user_input: str = "发布任务失败，请分析原因") -> Dict[str, Any]:
        """
        测试所有预定义场景（新功能）

        Args:
            user_input: 测试输入

        Returns:
            所有场景的测试结果
        """
        from ..core.configs.scenarios import ALL_SCENARIOS

        results = {}
        for scenario_name in ALL_SCENARIOS.keys():
            try:
                result = await self.core_service.test_scenario(scenario_name, user_input)
                results[scenario_name] = result
            except Exception as e:
                results[scenario_name] = {
                    "success": False,
                    "error": str(e)
                }

        return results

    def reset(self):
        """重置服务状态（新功能）"""
        self.core_service.reset()