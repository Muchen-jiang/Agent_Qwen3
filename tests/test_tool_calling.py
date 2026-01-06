#!/usr/bin/env python3
"""
工具调用测试脚本
用于验证模型是否能正确调用工具
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from agent import EnhancedLangGraphAgent
from tools import calculator, get_weather, get_current_time


def test_single_tool_call():
    """测试单个工具调用"""
    print("\n" + "="*80)
    print("测试 1: 单个工具调用 - 计算器")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=[calculator],
        verbose=True
    )

    test_queries = [
        "帮我计算 2 + 2",
        "计算 sqrt(16)",
        "10 * 5 等于多少？",
    ]

    for query in test_queries:
        print(f"\n{'─'*60}")
        print(f"查询: {query}")
        print('─'*60)
        result = agent.run(query, stream=True)

        # 检查是否调用了工具
        if result['tools_used']:
            print(f"✅ 成功调用工具: {result['tools_used']}")
        else:
            print(f"❌ 未调用工具！")

        print(f"响应: {result['response']}")


def test_weather_tool():
    """测试天气查询工具"""
    print("\n" + "="*80)
    print("测试 2: 天气查询工具")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=[get_weather],
        verbose=True
    )

    test_queries = [
        "北京今天天气怎么样？",
        "查询一下上海的天气",
    ]

    for query in test_queries:
        print(f"\n{'─'*60}")
        print(f"查询: {query}")
        print('─'*60)
        result = agent.run(query, stream=True)

        if result['tools_used']:
            print(f"✅ 成功调用工具: {result['tools_used']}")
        else:
            print(f"❌ 未调用工具！")


def test_multiple_tools():
    """测试多工具调用"""
    print("\n" + "="*80)
    print("测试 3: 多工具调用")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=[calculator, get_weather, get_current_time],
        verbose=True
    )

    query = "北京天气怎么样？另外帮我算一下 50 + 50"

    print(f"\n{'─'*60}")
    print(f"查询: {query}")
    print('─'*60)

    result = agent.run(query, stream=True)

    print(f"\n使用的工具: {result['tools_used']}")
    print(f"迭代次数: {result['iterations']}")

    if len(result['tools_used']) >= 2:
        print("✅ 成功调用多个工具")
    else:
        print(f"⚠️  只调用了 {len(result['tools_used'])} 个工具")


def test_tool_call_format():
    """测试工具调用格式的准确性"""
    print("\n" + "="*80)
    print("测试 4: 工具调用格式验证")
    print("="*80 + "\n")

    from utils import parse_qwen_response
    from langchain_core.messages import AIMessage

    # 模拟正确的工具调用
    test_cases = [
        {
            "content": '<tool_call>{"name": "calculator", "arguments": {"expression": "2+2"}}</tool_call>',
            "expected": True,
            "description": "正确的工具调用格式"
        },
        {
            "content": "让我计算一下：2+2=4",
            "expected": False,
            "description": "没有使用工具调用"
        },
        {
            "content": '<tool_call>{"name": "calculator", "args": {"expr": "2+2"}}</tool_call>',
            "expected": True,  # 虽然参数名错误，但格式能解析
            "description": "错误的参数名（但能解析）"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"内容: {test_case['content']}")

        message = AIMessage(content=test_case['content'])
        parsed = parse_qwen_response(message)

        has_tool_calls = bool(parsed.tool_calls)
        print(f"解析结果: {'✅ 检测到工具调用' if has_tool_calls else '❌ 未检测到工具调用'}")

        if has_tool_calls:
            print(f"工具调用详情: {parsed.tool_calls}")


def test_debug_prompt():
    """测试查看实际的系统提示词"""
    print("\n" + "="*80)
    print("测试 5: 查看系统提示词")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=[calculator, get_weather],
        verbose=False  # 关闭其他日志
    )

    print("系统提示词（前500字符）:")
    print("-" * 60)
    print(agent.system_prompt[:500])
    print("...")
    print("-" * 60)
    print(f"提示词总长度: {len(agent.system_prompt)} 字符")


def main():
    """运行所有测试"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              工具调用测试套件                                  ║
║          Tool Calling Test Suite                             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    tests = [
        ("1", "单工具调用", test_single_tool_call),
        ("2", "天气查询", test_weather_tool),
        ("3", "多工具调用", test_multiple_tools),
        ("4", "格式验证", test_tool_call_format),
        ("5", "查看提示词", test_debug_prompt),
    ]

    print("选择测试:")
    for key, name, _ in tests:
        print(f"  {key}. {name}")
    print("  0. 运行所有测试")
    print("  q. 退出")

    choice = input("\n请选择 (默认: 4): ").strip() or "4"

    if choice.lower() == 'q':
        return

    if choice == "0":
        for _, _, test_func in tests:
            test_func()
    else:
        for key, name, test_func in tests:
            if choice == key:
                test_func()
                break

    print("\n" + "="*80)
    print("测试完成")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
