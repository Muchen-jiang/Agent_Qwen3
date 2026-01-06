#!/usr/bin/env python3
"""
环境检查脚本
检查所有必需的依赖是否正确安装
"""
import sys
import importlib.util

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name

    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            return False, "未安装"

        # 尝试导入
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("环境依赖检查")
    print("="*60 + "\n")

    # 核心依赖
    core_packages = [
        ('torch', 'torch'),
        ('transformers', 'transformers'),
        ('accelerate', 'accelerate'),
    ]

    # LangChain 相关
    langchain_packages = [
        ('langchain', 'langchain'),
        ('langchain-core', 'langchain_core'),
        ('langchain-community', 'langchain_community'),
        ('langgraph', 'langgraph'),
        ('langchain-huggingface', 'langchain_huggingface'),
    ]

    # 工具库
    tool_packages = [
        ('faiss-cpu', 'faiss'),
        ('sentence-transformers', 'sentence_transformers'),
        ('duckduckgo-search', 'duckduckgo_search'),
        ('pypdf', 'pypdf'),
    ]

    all_ok = True

    def check_group(name, packages):
        nonlocal all_ok
        print(f"\n{name}:")
        print("-" * 60)
        for pkg_name, import_name in packages:
            ok, version = check_package(pkg_name, import_name)
            status = "✅" if ok else "❌"
            print(f"{status} {pkg_name:30s} {version}")
            if not ok:
                all_ok = False

    check_group("核心依赖", core_packages)
    check_group("LangChain 相关", langchain_packages)
    check_group("工具库", tool_packages)

    print("\n" + "="*60)

    if all_ok:
        print("✅ 所有依赖已正确安装！")
        print("\n下一步：")
        print("  1. 设置模型路径: export MODEL_PATH=/path/to/model")
        print("  2. 运行示例: python main.py")
    else:
        print("❌ 部分依赖缺失，请运行以下命令安装：")
        print("\n  pip install -r requirements.txt")
        print("\n或者单独安装缺失的包")

    print("="*60 + "\n")

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
