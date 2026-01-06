#!/usr/bin/env python3
"""
RAG示例 - 本地知识库检索
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import EnhancedLangGraphAgent
from tools import DEFAULT_TOOLS
from config import PROJECT_ROOT


def setup_knowledge_base():
    """设置知识库示例文档"""
    docs_dir = PROJECT_ROOT / "data" / "rag_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 创建多个示例文档
    documents = {
        "python_basics.txt": """
Python编程基础

Python是一种高级编程语言，由Guido van Rossum于1991年创建。

核心特性：
1. 简洁易读的语法
2. 动态类型系统
3. 自动内存管理
4. 丰富的标准库
5. 跨平台支持

基本数据类型：
- int: 整数
- float: 浮点数
- str: 字符串
- list: 列表
- dict: 字典
- tuple: 元组
- set: 集合

常用语法：
- 条件语句: if/elif/else
- 循环: for/while
- 函数定义: def
- 类定义: class
        """,

        "machine_learning.txt": """
机器学习基础

机器学习是人工智能的一个分支，让计算机能够从数据中学习。

主要类型：
1. 监督学习：使用标注数据训练模型
   - 分类：预测离散标签
   - 回归：预测连续值

2. 无监督学习：从未标注数据中发现模式
   - 聚类
   - 降维

3. 强化学习：通过与环境交互学习

常用算法：
- 线性回归
- 逻辑回归
- 决策树
- 随机森林
- 神经网络
- 支持向量机
- K-means聚类

流行框架：
- TensorFlow
- PyTorch
- Scikit-learn
- Keras
        """,

        "langgraph_guide.txt": """
LangGraph完整指南

LangGraph是构建有状态AI应用的强大框架。

架构组件：
1. StateGraph: 状态图的核心类
2. MessagesState: 消息状态管理
3. ToolNode: 工具执行节点
4. Checkpointer: 状态持久化

创建Agent的步骤：
1. 定义状态Schema
2. 创建工具函数
3. 实现Agent节点
4. 配置路由逻辑
5. 编译图并运行

高级特性：
- 条件边（Conditional Edges）
- 子图（Subgraphs）
- 人机协作（Human-in-the-loop）
- 流式输出（Streaming）
- 时间旅行调试

最佳实践：
1. 合理设计状态结构
2. 工具函数要单一职责
3. 充分的错误处理
4. 使用类型注解
5. 添加日志记录
        """
    }

    for filename, content in documents.items():
        file_path = docs_dir / filename
        if not file_path.exists():
            file_path.write_text(content.strip(), encoding='utf-8')
            print(f"✅ 创建文档: {filename}")

    print(f"\n📚 知识库位置: {docs_dir}\n")


def main():
    print("="*60)
    print("RAG知识库检索示例")
    print("="*60 + "\n")

    # 设置知识库
    setup_knowledge_base()

    # 创建Agent
    agent = EnhancedLangGraphAgent(
        tools=DEFAULT_TOOLS,
        verbose=True
    )

    # 知识库查询示例
    queries = [
        "Python有哪些基本数据类型？",
        "什么是监督学习？常用的监督学习算法有哪些？",
        "LangGraph的架构组件有哪些？",
        "如何创建一个LangGraph Agent？",
        "机器学习的流行框架有哪些？",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        result = agent.run(query, stream=True)
        print()


if __name__ == "__main__":
    main()
