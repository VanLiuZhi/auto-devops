"""
基础LLM接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseLLM(ABC):
    """所有LLM实现的基类"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._scenario_config = None

    @abstractmethod
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """子类必须实现的调用方法"""
        pass

    @property
    @abstractmethod
    def _llm_type(self) -> str:
        """返回模型类型标识"""
        pass

    def set_scenario_config(self, config: Dict[str, Any]):
        """设置场景配置，用于MockLLM动态响应"""
        self._scenario_config = config

    def reset(self):
        """重置模型状态"""
        pass

    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """统一的调用接口"""
        if self.verbose:
            print(f"\n--- {self._llm_type} 收到Prompt ---")
            print(prompt)
            print("--- End Prompt ---\n")

        return self._call(prompt, stop)