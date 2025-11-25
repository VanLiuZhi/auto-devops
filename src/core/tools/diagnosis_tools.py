"""
诊断工具定义
支持基于场景配置的动态响应
"""
import time
from typing import Dict, Any

from langchain_core.tools import tool


# 全局场景配置，用于工具的动态响应
_current_tool_scenario = None


def set_tool_scenario(scenario_config: Dict[str, Any]):
    """
    设置工具场景配置
    用于测试时模拟不同的工具响应
    """
    global _current_tool_scenario
    _current_tool_scenario = scenario_config


def get_tool_scenario():
    """获取当前工具场景配置"""
    return _current_tool_scenario


def clear_tool_scenario():
    """清除工具场景配置"""
    global _current_tool_scenario
    _current_tool_scenario = None


@tool
def get_build_log(input_str: str = "") -> str:
    """
    获取编译构建阶段的日志

    Args:
        input_str: 输入参数（通常为"_"）

    Returns:
        编译构建日志内容
    """
    # 检查是否有场景配置
    scenario = get_tool_scenario()
    if scenario and "build_log" in scenario:
        return scenario["build_log"]

    # 默认响应
    time.sleep(1)  # 模拟延迟
    return "[编译阶段日志] Maven 编译成功，没有错误。"


@tool
def get_k8s_log(input_str: str = "") -> str:
    """
    获取K8s部署阶段的日志

    Args:
        input_str: 输入参数（通常为"_"）

    Returns:
        K8s部署日志内容
    """
    # 检查是否有场景配置
    scenario = get_tool_scenario()
    if scenario and "k8s_log" in scenario:
        return scenario["k8s_log"]

    # 默认响应
    time.sleep(1)
    return "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。"


@tool
def get_service_log(input_str: str = "") -> str:
    """
    获取服务启动阶段的日志

    Args:
        input_str: 输入参数（通常为"_"）

    Returns:
        服务启动日志内容
    """
    # 检查是否有场景配置
    scenario = get_tool_scenario()
    if scenario and "service_log" in scenario:
        return scenario["service_log"]

    # 默认响应
    time.sleep(1)
    return "[服务启动日志] 服务正常启动。"


@tool
def knowledge_lookup(query: str) -> str:
    """
    从知识库中查找对应的解决方案

    Args:
        query: 查询关键词

    Returns:
        解决方案内容
    """
    # 检查是否有场景配置
    scenario = get_tool_scenario()
    if scenario and "knowledge_base" in scenario:
        knowledge_base = scenario["knowledge_base"]
        for key, solution in knowledge_base.items():
            if key in query:
                return solution

    # 默认知识库
    default_knowledge_base = {
        "健康检查失败": "请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。",
        "编译失败": "请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。",
        "运行时错误": "请检查服务启动日志中的详细错误堆栈，确认相关配置文件是否存在且格式正确，检查代码中的空值处理逻辑。"
    }

    time.sleep(1)
    for key, solution in default_knowledge_base.items():
        if key in query:
            return solution
    return "未找到相关的解决方案，请提供更多详细信息。"


# 预定义的工具场景配置
TOOL_SCENARIOS = {
    "k8s_health_check_failure": {
        "build_log": "[编译阶段日志] Maven 编译成功，没有错误。",
        "k8s_log": "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。",
        "service_log": "[服务启动日志] 服务正常启动。",
        "knowledge_base": {
            "健康检查失败": "请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
        }
    },

    "compilation_failure": {
        "build_log": "[编译阶段日志] Maven 编译失败！[ERROR] Failed to execute goal on project: Could not resolve dependencies...",
        "k8s_log": "[部署阶段日志] 未执行，因为编译失败。",
        "service_log": "[服务启动日志] 未执行，因为编译失败。",
        "knowledge_base": {
            "编译失败": "请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。"
        }
    },

    "runtime_failure": {
        "build_log": "[编译阶段日志] Maven 编译成功，没有错误。",
        "k8s_log": "[部署阶段日志] Helm 部署成功。",
        "service_log": "[服务启动日志] 服务启动失败！java.lang.NullPointerException: Cannot invoke \"String.length()\" because \"str\" is null",
        "knowledge_base": {
            "运行时错误": "请检查服务启动日志中的详细错误堆栈，确认相关配置文件是否存在且格式正确，检查代码中的空值处理逻辑。"
        }
    }
}


def configure_tools_for_scenario(scenario_name: str):
    """
    根据场景名称配置工具响应

    Args:
        scenario_name: 场景名称
    """
    if scenario_name in TOOL_SCENARIOS:
        set_tool_scenario(TOOL_SCENARIOS[scenario_name])
    else:
        clear_tool_scenario()