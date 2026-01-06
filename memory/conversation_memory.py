"""
对话记忆管理
实现多种记忆策略：窗口记忆、摘要记忆等
"""
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from config import agent_config
import logging

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    对话记忆管理器

    支持多种记忆策略：
    - 窗口记忆：保留最近N轮对话
    - 摘要记忆：对历史对话进行摘要
    - 缓冲记忆：保存所有历史
    """

    def __init__(
        self,
        memory_type: str = "window",
        window_size: int = None,
        enable_summary: bool = False
    ):
        """
        初始化记忆管理器

        Args:
            memory_type: 记忆类型 (window, buffer, summary)
            window_size: 窗口大小（仅用于window类型）
            enable_summary: 是否启用摘要
        """
        self.memory_type = memory_type
        self.window_size = window_size or agent_config.MEMORY_WINDOW_SIZE
        self.enable_summary = enable_summary
        self.messages: List[BaseMessage] = []
        self.summary: str = ""

    def add_message(self, message: BaseMessage) -> None:
        """添加消息到记忆"""
        self.messages.append(message)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """批量添加消息"""
        self.messages.extend(messages)

    def get_messages(self, include_system: bool = True) -> List[BaseMessage]:
        """
        获取记忆中的消息

        Args:
            include_system: 是否包含系统消息

        Returns:
            消息列表
        """
        if self.memory_type == "window":
            return self._get_window_messages(include_system)
        elif self.memory_type == "buffer":
            return self._get_buffer_messages(include_system)
        elif self.memory_type == "summary":
            return self._get_summary_messages(include_system)
        else:
            return self.messages

    def _get_window_messages(self, include_system: bool) -> List[BaseMessage]:
        """获取窗口记忆"""
        # 分离系统消息和其他消息
        system_msgs = [m for m in self.messages if isinstance(m, SystemMessage)]
        other_msgs = [m for m in self.messages if not isinstance(m, SystemMessage)]

        # 保留最近的N条消息
        recent_msgs = other_msgs[-self.window_size * 2:] if other_msgs else []

        if include_system and system_msgs:
            return system_msgs + recent_msgs
        return recent_msgs

    def _get_buffer_messages(self, include_system: bool) -> List[BaseMessage]:
        """获取缓冲记忆（所有消息）"""
        if not include_system:
            return [m for m in self.messages if not isinstance(m, SystemMessage)]
        return self.messages

    def _get_summary_messages(self, include_system: bool) -> List[BaseMessage]:
        """获取摘要记忆"""
        # TODO: 实现对话摘要功能
        # 这里可以使用LLM对历史对话进行摘要
        return self._get_window_messages(include_system)

    def clear(self) -> None:
        """清空记忆"""
        self.messages = []
        self.summary = ""
        logger.info("记忆已清空")

    def get_conversation_history(self) -> str:
        """获取对话历史的文本表示"""
        history = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                history.append(f"用户: {msg.content}")
            elif isinstance(msg, AIMessage):
                history.append(f"助手: {msg.content}")
        return "\n".join(history)

    def __len__(self) -> int:
        """返回记忆中的消息数量"""
        return len(self.messages)


class AgentState:
    """
    Agent状态管理器

    管理Agent运行时的状态信息，如：
    - 当前任务
    - 已执行的工具
    - 中间结果
    - 元数据
    """

    def __init__(self):
        self.current_task: str = ""
        self.executed_tools: List[Dict[str, Any]] = []
        self.intermediate_results: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.iteration_count: int = 0

    def add_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any
    ) -> None:
        """记录工具执行"""
        self.executed_tools.append({
            "tool_name": tool_name,
            "input": tool_input,
            "output": tool_output,
            "iteration": self.iteration_count
        })

    def increment_iteration(self) -> None:
        """增加迭代计数"""
        self.iteration_count += 1

    def reset(self) -> None:
        """重置状态"""
        self.current_task = ""
        self.executed_tools = []
        self.intermediate_results = {}
        self.iteration_count = 0
        logger.info("Agent状态已重置")

    def get_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            "current_task": self.current_task,
            "iteration_count": self.iteration_count,
            "tools_executed": len(self.executed_tools),
            "tool_names": [t["tool_name"] for t in self.executed_tools]
        }


__all__ = ['ConversationMemory', 'AgentState']
