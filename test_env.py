"""
环境变量配置测试脚本
"""
import os
from config import settings


def test_env_loading():
    """测试.env文件加载功能"""
    print("🔧 测试环境变量配置加载")
    print("=" * 50)

    # 检查.env文件是否存在
    if os.path.exists('.env'):
        print("✅ .env 文件存在")
    else:
        print("❌ .env 文件不存在")
        return False

    # 测试配置读取
    print("\n📋 配置项读取测试:")
    test_configs = [
        ('HOST', settings.HOST),
        ('PORT', settings.PORT),
        ('DEBUG', settings.DEBUG),
        ('RELOAD', settings.RELOAD),
        ('APP_NAME', settings.APP_NAME),
        ('API_PREFIX', settings.API_PREFIX),
        ('DIAGNOSIS_VERBOSE', settings.DIAGNOSIS_VERBOSE),
    ]

    for key, value in test_configs:
        print(f"   {key:20} = {value}")

    # 测试环境变量覆盖
    print("\n🔄 测试环境变量覆盖功能:")
    original_port = settings.PORT

    # 设置环境变量
    os.environ['PORT'] = '9999'

    # 重新创建settings实例
    from importlib import reload
    import config
    reload(config)

    new_settings = config.settings

    if new_settings.PORT == 9999:
        print(f"✅ 环境变量覆盖成功: PORT = {new_settings.PORT}")
    else:
        print(f"❌ 环境变量覆盖失败: PORT = {new_settings.PORT}")

    # 恢复原始设置
    os.environ['PORT'] = str(original_port)

    # 测试应用配置
    print("\n🚀 应用配置:")
    app_config = settings.app_config
    for key, value in app_config.items():
        print(f"   {key:15} = {value}")

    # 测试服务器配置
    print("\n🖥️  服务器配置:")
    server_config = settings.server_config
    for key, value in server_config.items():
        print(f"   {key:15} = {value}")

    print("\n🎉 环境变量配置测试完成！")
    return True


if __name__ == "__main__":
    test_env_loading()