#!/usr/bin/env python3
"""
简单示例 - 快速开始
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import EnhancedLangGraphAgent

# 创建Agent
agent = EnhancedLangGraphAgent()

# 简单对话
response = agent.chat("北京今天天气怎么样？")
print(f"AI: {response}")

# 计算任务
response = agent.chat("帮我计算 123 * 456")
print(f"AI: {response}")

# 搜索任务
response = agent.chat("搜索一下Python的最新版本")
print(f"AI: {response}")
