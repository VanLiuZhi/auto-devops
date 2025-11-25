"""
模型层：定义各种LLM实现和统一接口
"""
from .base_llm import BaseLLM
from .mock_llm import MockLLM
from .glm_llm import GLMLLM
from .model_factory import ModelFactory, ModelType