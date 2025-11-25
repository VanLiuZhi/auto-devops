#!/usr/bin/env python3
"""
新架构测试脚本
测试完整的ReAct Agent流程和场景切换功能
"""
import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.demo.diagnosis_core import DiagnosisService
from src.core.configs.scenarios import get_scenario_info, list_scenarios


async def test_single_scenario(scenario_name: str):
    """测试单个场景"""
    print(f"\n{'='*50}")
    print(f"测试场景: {scenario_name}")
    print(f"{'='*50}")

    # 获取场景信息
    scenario_info = get_scenario_info(scenario_name)
    if scenario_info:
        print(f"场景描述: {scenario_info['description']}")
        print(f"预期步骤: {' → '.join(scenario_info['expected_steps'])}")
        print(f"预期结果: {scenario_info['expected_result']}")

    # 创建诊断服务
    service = DiagnosisService(verbose=False)

    # 配置场景
    service.configure_scenario(scenario_name)

    # 测试流式诊断
    print(f"\n--- 流式诊断结果 ---")
    steps = []
    final_result = ""

    async for chunk in service.diagnose_stream("发布任务失败，请分析原因"):
        step_type = chunk.get("type", "")

        if step_type == "start":
            print(f"🚀 {chunk.get('message', '')}")

        elif step_type == "tool_call":
            tool_name = chunk.get("tool", "")
            print(f"🔧 调用工具: {tool_name}")

        elif step_type == "tool_result":
            tool_name = chunk.get("tool", "")
            result = chunk.get("result", "")[:50] + "..." if len(chunk.get("result", "")) > 50 else chunk.get("result", "")
            print(f"📄 {tool_name}结果: {result}")

        elif step_type == "final":
            final_result = chunk.get("content", "")
            print(f"✅ 最终结果:")
            print(final_result)

        elif step_type == "error":
            print(f"❌ 错误: {chunk.get('message', '')}")

        steps.append(chunk)

    # 测试同步诊断
    print(f"\n--- 同步诊断结果 ---")
    sync_result = await service.diagnose("发布任务失败，请分析原因")
    print(f"结果: {sync_result[:100]}..." if len(sync_result) > 100 else sync_result)

    # 验证结果一致性
    if final_result and sync_result:
        consistency = "✅ 一致" if final_result.strip() == sync_result.strip() else "❌ 不一致"
        print(f"\n结果一致性: {consistency}")

    return {
        "scenario": scenario_name,
        "steps_count": len([s for s in steps if s.get("type") in ["tool_call", "tool_result"]]),
        "has_final_result": bool(final_result),
        "sync_result_length": len(sync_result)
    }


async def test_scenario_switching():
    """测试场景切换功能"""
    print(f"\n{'='*50}")
    print("测试场景切换功能")
    print(f"{'='*50}")

    service = DiagnosisService(verbose=False)

    scenarios = ["k8s_health_check_failure", "compilation_failure", "runtime_failure"]

    for i, scenario_name in enumerate(scenarios, 1):
        print(f"\n--- 切换到场景 {i}: {scenario_name} ---")

        # 切换场景
        service.configure_scenario(scenario_name)

        # 获取服务信息
        info = service.get_service_info()
        print(f"当前场景: {info.get('current_scenario')}")
        print(f"模型类型: {info.get('model_type')}")

        # 快速测试
        result = await service.diagnose("测试输入")
        result_preview = result[:80] + "..." if len(result) > 80 else result
        print(f"结果预览: {result_preview}")


async def test_model_switching():
    """测试模型切换功能"""
    print(f"\n{'='*50}")
    print("测试模型切换功能")
    print(f"{'='*50}")

    service = DiagnosisService(verbose=False)

    # 测试Mock模型
    print("\n--- Mock模型 ---")
    service.switch_to_mock_model("k8s_health_check_failure")
    info = service.get_service_info()
    print(f"模型类型: {info.get('model_type')}")

    result = await service.diagnose("测试输入")
    print(f"Mock结果: {result[:50]}...")

    # 测试GLM模型（会失败因为没有API密钥）
    print("\n--- GLM模型 ---")
    service.switch_to_real_model()
    info = service.get_service_info()
    print(f"模型类型: {info.get('model_type')}")

    result = await service.diagnose("测试输入")
    print(f"GLM结果: {result}")


async def test_all_scenarios():
    """测试所有场景"""
    print(f"\n{'='*50}")
    print("测试所有预定义场景")
    print(f"{'='*50}")

    scenarios = list_scenarios()
    print(f"可用场景: {', '.join(scenarios)}")

    service = DiagnosisService(verbose=False)
    results = await service.test_all_scenarios("发布任务失败，请分析原因")

    print(f"\n--- 测试结果汇总 ---")
    for scenario_name, result in results.items():
        status = "✅ 成功" if result.get("success") else "❌ 失败"
        steps = result.get("total_steps", 0)
        final_result = result.get("final_result", "无结果")[:30] + "..."

        print(f"{scenario_name}: {status} (步骤数: {steps})")
        if not result.get("success"):
            print(f"  错误: {result.get('error', '未知错误')}")


async def main():
    """主测试函数"""
    print("🧪 新架构Agent测试开始")
    print("=" * 60)

    try:
        # 1. 测试单个场景
        print("\n🔍 第一部分：单个场景测试")
        test_scenarios = ["k8s_health_check_failure", "compilation_failure", "runtime_failure"]

        for scenario in test_scenarios:
            await test_single_scenario(scenario)

        # 2. 测试场景切换
        print("\n🔄 第二部分：场景切换测试")
        await test_scenario_switching()

        # 3. 测试模型切换
        print("\n🔧 第三部分：模型切换测试")
        await test_model_switching()

        # 4. 测试所有场景
        print("\n📊 第四部分：全场景测试")
        await test_all_scenarios()

        print(f"\n{'='*60}")
        print("🎉 所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())