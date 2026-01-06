#!/usr/bin/env python3
"""
最小测试脚本
验证核心导入是否正常工作
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试核心导入"""
    print("="*60)
    print("测试核心模块导入")
    print("="*60 + "\n")

    tests = []

    # 测试配置
    try:
        from config import model_config, agent_config
        print("✅ config 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"❌ config 模块导入失败: {e}")
        tests.append(False)

    # 测试工具
    try:
        from tools import DEFAULT_TOOLS
        print(f"✅ tools 模块导入成功 (加载了 {len(DEFAULT_TOOLS)} 个工具)")
        tests.append(True)
    except Exception as e:
        print(f"❌ tools 模块导入失败: {e}")
        tests.append(False)

    # 测试记忆
    try:
        from memory import ConversationMemory, AgentState
        print("✅ memory 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"❌ memory 模块导入失败: {e}")
        tests.append(False)

    # 测试工具函数
    try:
        from utils import format_input_for_qwen, parse_qwen_response
        print("✅ utils 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"❌ utils 模块导入失败: {e}")
        tests.append(False)

    # 测试Agent（不初始化模型）
    try:
        from agent.langgraph_agent import EnhancedLangGraphAgent
        print("✅ agent 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"❌ agent 模块导入失败: {e}")
        print(f"   详细错误: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        tests.append(False)

    print("\n" + "="*60)
    if all(tests):
        print("✅ 所有模块导入测试通过！")
        print("\n系统已准备就绪，可以运行完整示例。")
    else:
        print(f"❌ {tests.count(False)} 个模块导入失败")
        print("\n请检查依赖是否正确安装：")
        print("  python check_env.py")
    print("="*60 + "\n")

    return all(tests)

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
