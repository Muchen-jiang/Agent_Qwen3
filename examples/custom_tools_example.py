#!/usr/bin/env python3
"""
自定义工具示例
演示如何添加自定义工具
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.tools import tool
from agent import EnhancedLangGraphAgent
from tools import DEFAULT_TOOLS


# 定义自定义工具
@tool
def translate_to_english(text: str) -> str:
    """
    将中文翻译成英文（模拟）。

    Args:
        text: 要翻译的中文文本

    Returns:
        英文翻译结果
    """
    # 这里只是示例，实际应该调用翻译API
    translations = {
        "你好": "Hello",
        "谢谢": "Thank you",
        "再见": "Goodbye",
        "早上好": "Good morning",
    }

    result = translations.get(text, f"Translation of '{text}' (mock)")
    return f"英文翻译: {result}"


@tool
def get_random_quote() -> str:
    """
    获取一条随机的励志名言。

    Returns:
        励志名言
    """
    import random

    quotes = [
        "成功不是终点，失败也不是终结，继续前进的勇气才最重要。 - 温斯顿·丘吉尔",
        "你miss掉的100%的机会都是你没有尝试的。 - 韦恩·格雷茨基",
        "创新区分领导者和跟随者。 - 史蒂夫·乔布斯",
        "唯一不可能的事情就是你不去尝试的事情。",
        "今天的努力，决定明天的高度。",
    ]

    return random.choice(quotes)


def main():
    print("="*60)
    print("自定义工具示例")
    print("="*60 + "\n")

    # 创建包含自定义工具的Agent
    custom_tools = DEFAULT_TOOLS + [translate_to_english, get_random_quote]

    agent = EnhancedLangGraphAgent(
        tools=custom_tools,
        verbose=True
    )

    # 测试自定义工具
    queries = [
        "帮我翻译 '你好'",
        "给我一句励志名言",
        "翻译 '早上好' 并给我一句励志的话",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        result = agent.run(query, stream=True)


if __name__ == "__main__":
    main()
