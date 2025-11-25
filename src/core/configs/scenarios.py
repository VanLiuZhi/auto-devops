"""
场景配置：定义各种测试场景的完整配置
包含模型和工具的联动配置
"""

# 场景1：K8s健康检查失败
K8S_HEALTH_CHECK_FAILURE_SCENARIO = {
    "name": "k8s_health_check_failure",
    "description": "K8s健康检查失败场景 - 最常见的发布问题",
    "expected_steps": [
        "获取编译日志",
        "获取K8s部署日志",
        "发现健康检查失败",
        "获取服务启动日志",
        "查询知识库解决方案"
    ],
    "expected_result": "端口配置不一致的健康检查失败",

    "model": {
        "name": "k8s_health_check_failure",
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

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译成功，没有错误。",
        "k8s_log": "[部署阶段日志] Helm 部署成功，但 Pod 健康检查失败，端口8080无法访问。",
        "service_log": "[服务启动日志] 服务正常启动。",
        "knowledge_base": {
            "健康检查失败": "请检查平台配置的健康检查端口与代码中实际启动端口是否一致，通常在平台配置界面修改端口即可解决。"
        }
    }
}

# 场景2：编译失败
COMPILATION_FAILURE_SCENARIO = {
    "name": "compilation_failure",
    "description": "编译失败场景 - Maven构建问题",
    "expected_steps": [
        "获取编译日志",
        "发现编译错误",
        "查询知识库解决方案"
    ],
    "expected_result": "依赖项缺失或版本冲突的编译失败",

    "model": {
        "name": "compilation_failure",
        "sequence": [
            {"type": "thought", "content": "发布任务失败，让我先检查编译构建日志。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "发现了编译错误！Maven构建失败，依赖项缺失。让我查询解决方案。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "编译失败"},
            {"type": "final", "content": "问题阶段：编译构建\n原因分析：Maven编译失败，依赖项缺失或版本冲突\n解决方案：请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译失败！[ERROR] Failed to execute goal on project: Could not resolve dependencies for project com.example:app:jar:1.0.0: Failed to collect dependencies...",
        "k8s_log": "[部署阶段日志] 未执行，因为编译失败。",
        "service_log": "[服务启动日志] 未执行，因为编译失败。",
        "knowledge_base": {
            "编译失败": "请检查pom.xml文件中的依赖配置，确保所有依赖项版本正确且可用，必要时运行mvn clean install重新构建。"
        }
    }
}

# 场景3：运行时错误
RUNTIME_FAILURE_SCENARIO = {
    "name": "runtime_failure",
    "description": "运行时错误场景 - 服务启动后出现异常",
    "expected_steps": [
        "获取编译日志",
        "获取K8s部署日志",
        "获取服务启动日志",
        "发现运行时错误",
        "查询知识库解决方案"
    ],
    "expected_result": "配置缺失或空引用导致的运行时错误",

    "model": {
        "name": "runtime_failure",
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
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译成功，没有错误。",
        "k8s_log": "[部署阶段日志] Helm 部署成功。",
        "service_log": "[服务启动日志] 服务启动失败！java.lang.NullPointerException: Cannot invoke \"String.length()\" because \"str\" is null at com.example.service.ConfigService.loadConfig(ConfigService.java:45)",
        "knowledge_base": {
            "运行时错误": "请检查服务启动日志中的详细错误堆栈，确认相关配置文件是否存在且格式正确，检查代码中的空值处理逻辑。"
        }
    }
}

# 场景4：多步骤复杂问题
MULTI_STEP_COMPLEX_SCENARIO = {
    "name": "multi_step_complex",
    "description": "多步骤复杂问题场景 - 需要多次知识库查询",
    "expected_steps": [
        "获取编译日志",
        "获取K8s部署日志",
        "发现资源配置问题",
        "获取服务启动日志",
        "发现依赖服务不可用",
        "多次查询知识库"
    ],
    "expected_result": "复杂的配置和依赖问题",

    "model": {
        "name": "multi_step_complex",
        "sequence": [
            {"type": "thought", "content": "发布任务失败，让我全面检查各个环节。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译通过了，但有一些警告。检查部署情况。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "部署有些问题，资源配置不足。还需要检查服务启动情况。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "发现服务启动失败，依赖数据库不可用。需要查询相关解决方案。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "依赖服务不可用"},
            {"type": "thought", "content": "还有资源配置问题，需要再查询一下。"},
            {"type": "action", "tool": "knowledge_lookup", "input": "资源配置"},
            {"type": "final", "content": "问题阶段：服务部署和运行\n原因分析：1. Pod资源配置不足（CPU/内存限制） 2. 依赖数据库服务不可用\n解决方案：1. 增加Pod资源配置，调整CPU和内存限制 2. 检查数据库连接配置和服务可用性 3. 考虑添加就绪探针和启动探针确保依赖服务可用"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译成功，有警告：[WARNING] Some dependencies are marked as optional...",
        "k8s_log": "[部署阶段日志] Helm 部署部分成功，Warning: Pod has resource limits that may cause issues. Memory: 512Mi, CPU: 0.5",
        "service_log": "[服务启动日志] 服务启动失败！Connection refused: connect. Cannot connect to database at jdbc:mysql://db-service:3306/myapp",
        "knowledge_base": {
            "依赖服务不可用": "检查外部服务的网络连接配置，确保服务发现正常，验证连接参数和凭据。",
            "资源配置": "根据应用实际需求调整Pod的CPU和内存限制，监控资源使用情况，必要时设置资源请求(requests)和限制(limits)。"
        }
    }
}

# 场景5：正常流程（用于测试完整流程）
NORMAL_FLOW_SCENARIO = {
    "name": "normal_flow",
    "description": "正常流程场景 - 所有步骤都成功",
    "expected_steps": [
        "获取编译日志",
        "获取K8s部署日志",
        "获取服务启动日志",
        "确认所有步骤正常"
    ],
    "expected_result": "发布任务实际成功完成",

    "model": {
        "name": "normal_flow",
        "sequence": [
            {"type": "thought", "content": "用户说发布任务失败，但让我验证一下实际情况。"},
            {"type": "action", "tool": "get_build_log", "input": "_"},
            {"type": "thought", "content": "编译完全成功，没有任何问题。检查部署情况。"},
            {"type": "action", "tool": "get_k8s_log", "input": "_"},
            {"type": "thought", "content": "部署也成功了，Pod状态正常。检查服务启动。"},
            {"type": "action", "tool": "get_service_log", "input": "_"},
            {"type": "thought", "content": "所有步骤都正常，实际上发布任务是成功的。可能是前端显示问题。"},
            {"type": "final", "content": "诊断结果：发布任务实际上是成功的\n分析：编译、部署、服务启动所有步骤都正常完成\n建议：请检查前端界面的状态更新机制，可能是缓存或显示延迟导致的误导信息"}
        ]
    },

    "tools": {
        "build_log": "[编译阶段日志] Maven 编译成功，构建完成！",
        "k8s_log": "[部署阶段日志] Helm 部署成功！所有Pod处于Running状态。",
        "service_log": "[服务启动日志] 服务启动成功！所有健康检查通过，应用运行正常。",
        "knowledge_base": {
            "正常": "当所有步骤都正常时，可能是监控系统或前端显示的问题。"
        }
    }
}

# 所有场景的映射
ALL_SCENARIOS = {
    "k8s_health_check_failure": K8S_HEALTH_CHECK_FAILURE_SCENARIO,
    "compilation_failure": COMPILATION_FAILURE_SCENARIO,
    "runtime_failure": RUNTIME_FAILURE_SCENARIO,
    "multi_step_complex": MULTI_STEP_COMPLEX_SCENARIO,
    "normal_flow": NORMAL_FLOW_SCENARIO
}

def get_scenario(scenario_name: str):
    """获取指定场景配置"""
    return ALL_SCENARIOS.get(scenario_name)

def list_scenarios():
    """列出所有可用场景"""
    return list(ALL_SCENARIOS.keys())

def get_scenario_info(scenario_name: str) -> dict:
    """获取场景的简要信息"""
    scenario = get_scenario(scenario_name)
    if scenario:
        return {
            "name": scenario["name"],
            "description": scenario["description"],
            "expected_steps": scenario["expected_steps"],
            "expected_result": scenario["expected_result"]
        }
    return None