"""
前端功能测试脚本
"""
import requests
import json
import time


def test_frontend_features():
    """测试前端相关功能"""
    base_url = "http://localhost:8002"

    print("🎨 测试前端功能...")

    # 测试前端页面加载
    try:
        print("\n1. 测试前端页面加载...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "Auto DevOps" in response.text:
            print("✅ 前端页面加载成功")
        else:
            print(f"❌ 前端页面加载失败 (状态码: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端页面连接失败: {e}")
        print("💡 请确保服务正在运行: python main.py")
        return False

    # 测试静态文件服务
    try:
        print("\n2. 测试静态文件服务...")
        response = requests.get(f"{base_url}/static/index.html", timeout=5)
        if response.status_code == 200:
            print("✅ 静态文件服务正常")
        else:
            print(f"❌ 静态文件服务失败 (状态码: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ 静态文件服务失败: {e}")

    # 测试API健康检查
    try:
        print("\n3. 测试API健康检查...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ API健康检查正常")
            print(f"   服务状态: {result.get('status')}")
        else:
            print(f"❌ API健康检查失败 (状态码: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ API健康检查失败: {e}")

    # 测试聊天接口
    try:
        print("\n4. 测试聊天接口...")
        chat_data = {
            "message": "测试前端集成",
            "user_id": "frontend_test"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print("✅ 聊天接口正常")
            print(f"   响应状态: {result.get('status')}")
            print(f"   AI回复: {result.get('response', '')[:50]}...")
        else:
            print(f"❌ 聊天接口失败 (状态码: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ 聊天接口失败: {e}")

    print("\n🎉 前端功能测试完成！")
    print(f"🌐 请在浏览器中访问: {base_url}/")
    return True


if __name__ == "__main__":
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)

    test_frontend_features()