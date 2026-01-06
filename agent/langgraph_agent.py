"""
LangGraph Agent核心
实现基于LangGraph的增强型ReAct Agent
"""
from typing import List, Optional, Dict, Any, Callable, TYPE_CHECKING
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import create_react_agent

# 类型检查时导入，避免运行时错误
if TYPE_CHECKING:
    from langgraph.graph import CompiledGraph

from config import agent_config
from utils import model_loader, format_input_for_qwen, parse_qwen_response
from memory import ConversationMemory, AgentState
from tools import DEFAULT_TOOLS
from .prompt_engineer import ToolPromptBuilder

import logging

logger = logging.getLogger(__name__)


class EnhancedLangGraphAgent:
    """
    增强型LangGraph Agent

    特性:
    - 支持多种工具集成（搜索、RAG、计算等）
    - 对话记忆管理
    - 状态跟踪
    - 流式输出
    - 错误处理和重试
    """

    def __init__(
        self,
        tools: Optional[List] = None,
        system_prompt: Optional[str] = None,
        enable_memory: bool = True,
        memory_type: str = "window",
        verbose: bool = True
    ):
        """
        初始化Agent

        Args:
            tools: 工具列表，默认使用DEFAULT_TOOLS
            system_prompt: 系统提示词
            enable_memory: 是否启用记忆
            memory_type: 记忆类型 (window, buffer, summary)
            verbose: 是否输出详细日志
        """
        self.tools = tools or DEFAULT_TOOLS
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.enable_memory = enable_memory
        self.verbose = verbose

        # 初始化组件
        self.chat_model = model_loader.chat_model
        self.tokenizer = model_loader.tokenizer

        # 初始化记忆和状态
        self.memory = ConversationMemory(memory_type=memory_type) if enable_memory else None
        self.state = AgentState()

        # 构建Agent图
        self.agent_graph = self._build_agent_graph()

        logger.info(f"✅ Agent初始化完成，加载了 {len(self.tools)} 个工具")

        # 如果是verbose模式，打印系统提示词
        if self.verbose:
            logger.debug(f"\n{'='*60}\n系统提示词:\n{'='*60}\n{self.system_prompt}\n{'='*60}\n")

    def _default_system_prompt(self) -> str:
        """
        默认系统提示词 - 使用增强的提示词工程
        包含详细的工具描述和few-shot示例
        """
        return ToolPromptBuilder.build_enhanced_system_prompt(self.tools)

    def _build_agent_graph(self):
        """
        构建Agent执行图

        创建处理链：输入格式化 -> 模型调用 -> 输出解析
        """
        logger.info("🔨 正在构建Agent执行图...")

        # 1. 绑定工具
        llm_with_tools = self.chat_model.bind_tools(self.tools)

        # 2. 构建处理链
        model_chain = (
            RunnableLambda(format_input_for_qwen)
            | llm_with_tools
            | parse_qwen_response
        )

        # 3. 创建ReAct Agent图
        agent_graph = create_react_agent(
            model=model_chain,
            tools=self.tools
        )

        logger.info("✅ Agent执行图构建完成")
        return agent_graph

    def run(
        self,
        query: str,
        stream: bool = None,
        max_iterations: int = None
    ) -> Dict[str, Any]:
        """
        运行Agent

        Args:
            query: 用户查询
            stream: 是否流式输出，默认使用配置值
            max_iterations: 最大迭代次数，默认使用配置值

        Returns:
            包含结果和元数据的字典
        """
        stream = stream if stream is not None else agent_config.ENABLE_STREAMING
        max_iterations = max_iterations or agent_config.MAX_ITERATIONS

        # 重置状态
        self.state.reset()
        self.state.current_task = query

        # 构建输入消息
        messages = [SystemMessage(content=self.system_prompt)]

        # 添加记忆中的历史消息
        if self.enable_memory and len(self.memory) > 0:
            messages.extend(self.memory.get_messages(include_system=False))

        # 添加当前查询
        messages.append(HumanMessage(content=query))

        # 准备输入
        inputs = {"messages": messages}

        # 运行Agent
        try:
            if stream:
                return self._run_streaming(inputs, query)
            else:
                return self._run_batch(inputs, query)

        except Exception as e:
            logger.error(f"❌ Agent运行失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def _run_streaming(self, inputs: Dict, query: str) -> Dict[str, Any]:
        """流式运行"""
        logger.info(f"🚀 开始流式执行: {query}\n")
        print("=" * 60)

        final_response = ""
        tool_calls_made = []

        for event in self.agent_graph.stream(inputs, stream_mode="values"):
            message = event["messages"][-1]

            # 增加迭代计数
            self.state.increment_iteration()

            if message.type == "human":
                if self.verbose:
                    print(f"👤 [用户] {message.content}")
                    print("-" * 60)

            elif message.type == "ai":
                if message.tool_calls:
                    if self.verbose:
                        print(f"🤖 [AI] 决定调用 {len(message.tool_calls)} 个工具:")
                        for tc in message.tool_calls:
                            print(f"   📞 {tc['name']}")
                            print(f"      参数: {tc['args']}")
                            tool_calls_made.append(tc['name'])
                        print("-" * 60)
                else:
                    final_response = message.content
                    if self.verbose:
                        print(f"🤖 [AI] {final_response}")
                        print("-" * 60)

            elif message.type == "tool":
                if self.verbose:
                    content_preview = (
                        message.content[:200] + "..."
                        if len(message.content) > 200
                        else message.content
                    )
                    print(f"🔧 [工具结果] {content_preview}")
                    print("-" * 60)

        print("=" * 60)

        # 保存到记忆
        if self.enable_memory:
            self.memory.add_message(HumanMessage(content=query))
            self.memory.add_message(AIMessage(content=final_response))

        return {
            "success": True,
            "response": final_response,
            "query": query,
            "tools_used": tool_calls_made,
            "iterations": self.state.iteration_count,
            "state_summary": self.state.get_summary()
        }

    def _run_batch(self, inputs: Dict, query: str) -> Dict[str, Any]:
        """批量运行（非流式）"""
        logger.info(f"🚀 开始执行: {query}")

        result = self.agent_graph.invoke(inputs)
        final_message = result["messages"][-1]

        response = final_message.content if hasattr(final_message, 'content') else str(final_message)

        # 保存到记忆
        if self.enable_memory:
            self.memory.add_message(HumanMessage(content=query))
            self.memory.add_message(AIMessage(content=response))

        return {
            "success": True,
            "response": response,
            "query": query,
            "state_summary": self.state.get_summary()
        }

    def chat(self, message: str, **kwargs) -> str:
        """
        简化的聊天接口

        Args:
            message: 用户消息
            **kwargs: 传递给run的额外参数

        Returns:
            AI响应文本
        """
        result = self.run(message, **kwargs)
        return result.get("response", "抱歉，我无法处理这个请求。")

    def clear_memory(self) -> None:
        """清空对话记忆"""
        if self.memory:
            self.memory.clear()
            logger.info("✅ 对话记忆已清空")

    def get_conversation_history(self) -> str:
        """获取对话历史"""
        if self.memory:
            return self.memory.get_conversation_history()
        return ""

    def add_tool(self, tool: Callable) -> None:
        """
        动态添加工具

        Args:
            tool: 工具函数（需要用@tool装饰）
        """
        self.tools.append(tool)
        # 重建Agent图
        self.agent_graph = self._build_agent_graph()
        logger.info(f"✅ 已添加工具: {tool.name}")


__all__ = ['EnhancedLangGraphAgent']
