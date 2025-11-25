"""
Agent配置：预定义的Agent配置模板
"""

# 开发环境配置
DEVELOPMENT_CONFIG = {
    "model": {
        "type": "scenario_based_mock",
        "params": {
            "scenario_name": "k8s_health_check_failure"
        }
    },
    "agent": {
        "verbose": True,
        "max_iterations": 10
    }
}

# 生产环境配置
PRODUCTION_CONFIG = {
    "model": {
        "type": "glm",
        "params": {
            "api_key": None  # 需要从环境变量或配置文件设置
        }
    },
    "agent": {
        "verbose": False,
        "max_iterations": 15
    }
}

# 测试环境配置
TEST_CONFIG = {
    "model": {
        "type": "mock",
        "params": {
            "scenario_name": "default"
        }
    },
    "agent": {
        "verbose": True,
        "max_iterations": 5
    }
}

# 性能测试配置
PERFORMANCE_TEST_CONFIG = {
    "model": {
        "type": "scenario_based_mock",
        "params": {
            "scenario_name": "multi_step_complex"
        }
    },
    "agent": {
        "verbose": False,
        "max_iterations": 20
    }
}

# 多场景测试配置
MULTI_SCENARIO_TEST_CONFIG = {
    "scenarios": [
        "k8s_health_check_failure",
        "compilation_failure",
        "runtime_failure",
        "normal_flow"
    ],
    "common_agent_config": {
        "verbose": True,
        "max_iterations": 10
    }
}

# 所有配置的映射
ALL_CONFIGS = {
    "development": DEVELOPMENT_CONFIG,
    "production": PRODUCTION_CONFIG,
    "test": TEST_CONFIG,
    "performance_test": PERFORMANCE_TEST_CONFIG,
    "multi_scenario_test": MULTI_SCENARIO_TEST_CONFIG
}

def get_config(config_name: str):
    """获取指定配置"""
    return ALL_CONFIGS.get(config_name)

def list_configs():
    """列出所有可用配置"""
    return list(ALL_CONFIGS.keys())