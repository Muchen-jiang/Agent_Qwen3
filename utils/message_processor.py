"""
消息处理器
处理LangChain消息格式，解决Qwen模型的兼容性问题
"""
import re
import json
import uuid
from typing import List, Union
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    SystemMessage,
    BaseMessage
)
import logging

logger = logging.getLogger(__name__)


def format_input_for_qwen(input_data: Union[dict, list, BaseMessage]) -> List[BaseMessage]:
    """
    输入端中间件：将ToolMessage转换为HumanMessage

    LangChain严格要求对话必须以HumanMessage结尾，且某些版本不识别ToolMessage。
    此函数将所有ToolMessage转换为带"Observation:"前缀的HumanMessage。

    Args:
        input_data: 输入数据，可以是字典、列表或单个消息

    Returns:
        处理后的消息列表
    """
    # 1. 解包input_data
    if isinstance(input_data, dict) and "messages" in input_data:
        original_messages = list(input_data["messages"])
    elif isinstance(input_data, list):
        original_messages = list(input_data)
    else:
        original_messages = [input_data]

    new_messages = []

    # 2. 遍历并转换
    for msg in original_messages:
        if isinstance(msg, ToolMessage):
            # 将工具结果伪装成用户的"观察报告"
            new_content = f"Observation: {msg.content}"
            new_messages.append(HumanMessage(content=new_content))
        else:
            # 其他消息保持不变
            new_messages.append(msg)

    return new_messages


def parse_qwen_response(ai_message: AIMessage) -> AIMessage:
    """
    输出端中间件：清洗模型输出，提取<tool_call>，忽略<think>

    Qwen模型倾向于先输出思考过程，这会干扰标准XML解析器。
    此函数使用正则表达式提取工具调用JSON，并重构为标准AIMessage。

    Args:
        ai_message: AI返回的原始消息

    Returns:
        处理后的AIMessage
    """
    content = ai_message.content

    # 如果已经有tool_calls，直接返回
    if ai_message.tool_calls:
        return ai_message

    # 提取所有<tool_call>标签
    pattern = r"<tool_call>(.*?)</tool_call>"
    matches = re.findall(pattern, content, re.DOTALL)

    extracted_tool_calls = []

    for match in matches:
        try:
            json_str = match.strip()
            tool_data = json.loads(json_str)

            extracted_tool_calls.append({
                "name": tool_data["name"],
                "args": tool_data["arguments"],
                "id": f"call_{uuid.uuid4().hex[:8]}"
            })

        except json.JSONDecodeError as e:
            logger.warning(f"解析工具调用JSON失败: {e}\n内容: {match}")
        except KeyError as e:
            logger.warning(f"工具调用缺少必需字段: {e}\n数据: {tool_data}")
        except Exception as e:
            logger.error(f"处理工具调用时发生未知错误: {e}")

    # 如果提取到了工具调用，返回新的AIMessage
    if extracted_tool_calls:
        return AIMessage(content=content, tool_calls=extracted_tool_calls)

    return ai_message


def inspect_messages(messages: List[BaseMessage], title: str = "消息检查") -> None:
    """
    调试工具：打印消息列表的详细信息

    Args:
        messages: 消息列表
        title: 标题
    """
    logger.debug(f"\n{'='*60}")
    logger.debug(f"🕵️  {title}")
    logger.debug(f"{'='*60}")

    for idx, msg in enumerate(messages, 1):
        msg_type = msg.__class__.__name__
        content_preview = msg.content[:100] if len(msg.content) > 100 else msg.content

        logger.debug(f"{idx}. [{msg_type}]")
        logger.debug(f"   内容: {content_preview}")

        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            logger.debug(f"   工具调用: {len(msg.tool_calls)} 个")
            for tc in msg.tool_calls:
                logger.debug(f"     - {tc['name']}: {tc['args']}")

        if isinstance(msg, ToolMessage):
            logger.debug(f"   工具调用ID: {msg.tool_call_id}")

    logger.debug(f"{'='*60}\n")


__all__ = [
    'format_input_for_qwen',
    'parse_qwen_response',
    'inspect_messages'
]
