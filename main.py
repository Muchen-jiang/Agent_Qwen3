#!/usr/bin/env python3
"""
主运行文件
展示如何使用EnhancedLangGraphAgent
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import EnhancedLangGraphAgent
from tools import ALL_TOOLS, DEFAULT_TOOLS
from config import log_config

# 配置日志
logging.basicConfig(
    level=getattr(logging, log_config.LOG_LEVEL),
    format=log_config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler(log_config.LOG_FILE)  # 取消注释以启用文件日志
    ]
)

logger = logging.getLogger(__name__)


def demo_basic_usage():
    """示例1: 基础使用"""
    print("\n" + "="*80)
    print("示例1: 基础使用 - 天气查询和计算")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=DEFAULT_TOOLS,
        enable_memory=True,
        verbose=True
    )

    # 测试查询
    queries = [
        "北京今天天气怎么样？",
        "帮我计算 123 + 456 的结果",
        "sqrt(144) 等于多少？"
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        result = agent.run(query, stream=True)
        print(f"\n结果: {result['response']}\n")


def demo_web_search():
    """示例2: 网络搜索"""
    print("\n" + "="*80)
    print("示例2: 网络搜索")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=DEFAULT_TOOLS,
        verbose=True
    )

    queries = [
        "帮我搜索一下2024年诺贝尔物理学奖获得者是谁",
        "搜索一下Python 3.12的新特性有哪些",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        result = agent.run(query, stream=True)


def demo_knowledge_base():
    """示例3: 知识库检索"""
    print("\n" + "="*80)
    print("示例3: 知识库检索")
    print("="*80 + "\n")

    # 首先创建一些示例文档
    docs_dir = project_root / "data" / "rag_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 创建示例文档
    sample_doc = docs_dir / "example.txt"
    if not sample_doc.exists():
        sample_doc.write_text("""
LangGraph 简介

LangGraph 是一个用于构建有状态的、多参与者的 LLM 应用程序的库。
它基于 LangChain 构建，提供了更灵活的控制流和状态管理。

核心概念：
1. **图（Graph）**: 应用程序的整体结构
2. **节点（Node）**: 执行特定操作的单元
3. **边（Edge）**: 连接节点的路径
4. **状态（State）**: 在节点之间传递的数据

主要特性：
- 循环和分支控制流
- 持久化状态
- 人机协作
- 流式输出
- 时间旅行和回放

使用场景：
- ReAct Agent
- 多智能体系统
- 复杂的工作流编排
- 需要人类反馈的应用
        """, encoding='utf-8')
        print(f"✅ 创建示例文档: {sample_doc}")

    agent = EnhancedLangGraphAgent(
        tools=DEFAULT_TOOLS,
        verbose=True
    )

    queries = [
        "什么是LangGraph？",
        "LangGraph有哪些核心概念？",
        "LangGraph的主要特性是什么？"
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        result = agent.run(query, stream=True)


def demo_multi_turn_conversation():
    """示例4: 多轮对话"""
    print("\n" + "="*80)
    print("示例4: 多轮对话（带记忆）")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=DEFAULT_TOOLS,
        enable_memory=True,
        memory_type="window",
        verbose=True
    )

    conversation = [
        "你好，我想了解一下今天北京的天气",
        "那上海呢？",  # 测试上下文理解
        "帮我计算 50 + 50",
        "再加上刚才那个结果",  # 测试记忆
    ]

    for query in conversation:
        print(f"\n{'='*60}")
        print(f"用户: {query}")
        print('='*60)
        result = agent.run(query, stream=True)

    print("\n" + "="*60)
    print("对话历史:")
    print("="*60)
    print(agent.get_conversation_history())


def demo_complex_task():
    """示例5: 复杂任务"""
    print("\n" + "="*80)
    print("示例5: 复杂任务 - 综合使用多个工具")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=ALL_TOOLS,  # 使用所有工具
        verbose=True
    )

    query = """
    帮我完成以下任务：
    1. 搜索一下 "LangGraph 最新版本"
    2. 查询当前时间
    3. 计算 2024 - 2020 等于多少年
    4. 北京的天气如何
    """

    print(f"复杂任务: {query}\n")
    result = agent.run(query, stream=True)

    print(f"\n{'='*60}")
    print("任务完成统计:")
    print(f"  - 使用的工具: {result['tools_used']}")
    print(f"  - 迭代次数: {result['iterations']}")
    print('='*60)


def interactive_mode():
    """交互模式"""
    print("\n" + "="*80)
    print("交互模式 - 输入 'quit' 或 'exit' 退出")
    print("="*80 + "\n")

    agent = EnhancedLangGraphAgent(
        tools=DEFAULT_TOOLS,
        enable_memory=True,
        verbose=True
    )

    print("可用命令:")
    print("  - 'clear': 清空对话记忆")
    print("  - 'history': 查看对话历史")
    print("  - 'quit' / 'exit': 退出\n")

    while True:
        try:
            user_input = input("\n👤 你: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break

            if user_input.lower() == 'clear':
                agent.clear_memory()
                print("✅ 记忆已清空")
                continue

            if user_input.lower() == 'history':
                print("\n对话历史:")
                print("="*60)
                print(agent.get_conversation_history())
                print("="*60)
                continue

            # 运行Agent
            result = agent.run(user_input, stream=True)

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            logger.error(f"错误: {e}")
            print(f"❌ 发生错误: {e}")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        增强型 LangGraph Agent 演示系统                        ║
║        Enhanced LangGraph Agent Demo System                  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    demos = {
        "1": ("基础使用", demo_basic_usage),
        "2": ("网络搜索", demo_web_search),
        "3": ("知识库检索", demo_knowledge_base),
        "4": ("多轮对话", demo_multi_turn_conversation),
        "5": ("复杂任务", demo_complex_task),
        "6": ("交互模式", interactive_mode),
    }

    print("请选择演示模式:")
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    print("  0. 运行所有演示（除交互模式）")
    print("  q. 退出")

    choice = input("\n请输入选项 (默认: 6): ").strip() or "6"

    if choice.lower() == 'q':
        print("👋 再见！")
        return

    if choice == "0":
        # 运行所有演示（除了交互模式）
        for key in ["1", "2", "3", "4", "5"]:
            demos[key][1]()
    elif choice in demos:
        demos[choice][1]()
    else:
        print(f"❌ 无效选项: {choice}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"程序异常: {e}")
        import traceback
        traceback.print_exc()
