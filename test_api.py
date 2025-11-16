"""
API测试脚本
"""
import requests
import json
import time


def test_api():
    """测试API接口"""
    base_url = "http://localhost:8002"

    print("🧪 开始测试API...")

    # 测试健康检查
    try:
        print("\n1. 测试健康检查接口...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查 - 成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查 - 失败 (状态码: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ 健康检查 - 连接失败: {e}")
        return False

    # 测试聊天接口
    try:
        print("\n2. 测试聊天接口...")
        chat_data = {
            "message": "发布任务失败，请分析原因",
            "user_id": "test_user"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=30)
        if response.status_code == 200:
            print("✅ 聊天接口 - 成功")
            result = response.json()
            print(f"   状态: {result.get('status')}")
            print(f"   响应: {result.get('response', '')[:100]}...")
        else:
            print(f"❌ 聊天接口 - 失败 (状态码: {response.status_code})")
            print(f"   响应: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 聊天接口 - 连接失败: {e}")

    print("\n🎉 API测试完成！")
    return True


if __name__ == "__main__":
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)

    test_api()