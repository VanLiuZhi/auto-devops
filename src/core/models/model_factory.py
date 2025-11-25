"""
模型工厂：统一管理不同类型的LLM创建
"""
from enum import Enum
from typing import Dict, Any

from .base_llm import BaseLLM
from .mock_llm import MockLLM, create_mock_llm
from .glm_llm import GLMLLM


class ModelType(Enum):
    """模型类型枚举"""
    MOCK = "mock"
    GLM = "glm"
    SCENARIO_BASED_MOCK = "scenario_based_mock"


class ModelFactory:
    """
    模型工厂类
    负责根据配置创建不同类型的LLM实例
    """

    @staticmethod
    def create_model(
        model_type: ModelType,
        verbose: bool = False,
        **kwargs
    ) -> BaseLLM:
        """
        创建指定类型的LLM实例

        Args:
            model_type: 模型类型
            verbose: 是否输出详细日志
            **kwargs: 其他模型特定参数

        Returns:
            LLM实例
        """
        if model_type == ModelType.MOCK:
            return MockLLM(verbose=verbose, scenario_name=kwargs.get("scenario_name", "default"))

        elif model_type == ModelType.GLM:
            api_key = kwargs.get("api_key")
            return GLMLM(api_key=api_key, verbose=verbose)

        elif model_type == ModelType.SCENARIO_BASED_MOCK:
            scenario_name = kwargs.get("scenario_name", "k8s_health_check_failure")
            return create_mock_llm(scenario_name, verbose)

        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> BaseLLM:
        """
        从配置字典创建LLM实例

        Args:
            config: 配置字典，包含模型类型和参数

        Returns:
            LLM实例
        """
        model_type_str = config.get("type", "mock")
        try:
            model_type = ModelType(model_type_str)
        except ValueError:
            raise ValueError(f"未知的模型类型: {model_type_str}")

        return ModelFactory.create_model(
            model_type=model_type,
            verbose=config.get("verbose", False),
            **config.get("params", {})
        )