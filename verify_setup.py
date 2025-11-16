"""
环境验证脚本
验证项目设置是否正确
"""
import sys
import os


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)")
        return False


def check_virtual_env():
    """检查虚拟环境"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境已激活")
        return True
    else:
        print("⚠️  建议使用虚拟环境")
        return False


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'requests',
        'langchain_core'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")

    if missing_packages:
        print(f"\n💡 安装缺失的依赖:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    return True


def check_project_structure():
    """检查项目结构"""
    required_files = [
        'main.py', 'config.py', 'requirements.txt',
        'src/__init__.py', 'src/demo/__init__.py',
        'src/demo/web_service.py', 'src/demo/diagnosis_core.py'
    ]

    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} 不存在")

    return len(missing_files) == 0


def check_imports():
    """检查关键导入"""
    try:
        from main import create_app
        from src.demo.web_service import router
        from src.demo.diagnosis_core import DiagnosisService
        print("✅ 关键模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def main():
    """主验证函数"""
    print("🔍 Auto DevOps 环境验证")
    print("=" * 40)

    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("依赖包", check_dependencies),
        ("项目结构", check_project_structure),
        ("模块导入", check_imports)
    ]

    results = []
    for name, check_func in checks:
        print(f"\n📋 检查 {name}:")
        result = check_func()
        results.append(result)

    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 验证通过 ({passed}/{total})")
        print("\n🚀 启动服务:")
        print("   python main.py")
        print("\n📚 访问API文档:")
        print("   http://localhost:8002/docs")
    else:
        print(f"⚠️  验证未完全通过 ({passed}/{total})")
        print("请根据上述提示修复问题")


if __name__ == "__main__":
    main()