"""
工具管理器：统一管理诊断工具
"""
from typing import Dict, List, Any

from .diagnosis_tools import get_build_log, get_k8s_log, get_service_log, knowledge_lookup


class ToolManager:
    """
    工具管理器
    负责工具的注册、管理和调用
    """

    def __init__(self):
        self._tools = {
            "get_build_log": get_build_log,
            "get_k8s_log": get_k8s_log,
            "get_service_log": get_service_log,
            "knowledge_lookup": knowledge_lookup
        }

    def get_tools(self) -> List:
        """获取所有工具"""
        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self._tools.keys())

    def get_tool(self, name: str):
        """根据名称获取工具"""
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools

    def invoke_tool(self, tool_name: str, input_data: str = "") -> str:
        """
        调用指定工具

        Args:
            tool_name: 工具名称
            input_data: 输入数据

        Returns:
            工具执行结果

        Raises:
            ValueError: 如果工具不存在
        """
        if not self.has_tool(tool_name):
            raise ValueError(f"工具 '{tool_name}' 不存在")

        tool = self.get_tool(tool_name)

        # 某些工具使用固定参数
        if tool_name in ["get_build_log", "get_k8s_log", "get_service_log"]:
            return tool.invoke("_")
        else:
            return tool.invoke(input_data)

    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        获取所有工具的描述信息

        Returns:
            工具名称到描述的映射
        """
        descriptions = {}
        for name, tool in self._tools.items():
            descriptions[name] = tool.description
        return descriptions

    def register_tool(self, name: str, tool):
        """
        注册新工具

        Args:
            name: 工具名称
            tool: 工具对象
        """
        self._tools[name] = tool

    def unregister_tool(self, name: str):
        """
        注销工具

        Args:
            name: 工具名称
        """
        if name in self._tools:
            del self._tools[name]


# 全局工具管理器实例
tool_manager = ToolManager()