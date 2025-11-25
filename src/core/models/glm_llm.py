"""
GLM-4.6真实LLM实现
"""
import requests
from typing import List, Optional

from .base_llm import BaseLLM


class GLMLLM(BaseLLM):
    """
    智谱GLM-4.6大模型的LLM实现
    基于base/agent.py中的GLMLLM改造
    """

    def __init__(self, api_key: str = None, verbose: bool = False):
        super().__init__(verbose)
        # 从环境变量或默认值获取API密钥
        self.api_key = api_key or "xxx."  # 需要用户提供真实的API密钥
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4.6"

    @property
    def _llm_type(self) -> str:
        return "glm-4-6"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        调用GLM-4.6 API
        """
        if self.api_key == "xxx.":
            return f"Final Answer: 未配置有效的GLM-4.6 API密钥，请设置正确的api_key参数。"

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