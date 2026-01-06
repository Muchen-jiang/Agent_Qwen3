"""
基础工具集
包含计算器、天气、时间等常用工具
"""
from langchain_core.tools import tool
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


@tool
def calculator(expression: str) -> str:
    """
    计算数学表达式的结果。支持基本运算和常用数学函数。

    Args:
        expression: 数学表达式，如 "2 + 2", "sqrt(16)", "sin(3.14/2)"

    Returns:
        计算结果

    Examples:
        - calculator("2 + 2") -> "4"
        - calculator("sqrt(16)") -> "4.0"
        - calculator("10 ** 2") -> "100"
    """
    try:
        # 安全的数学函数白名单
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            # 数学函数
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }

        # 使用 eval，但限制命名空间以确保安全
        result = eval(expression, {"__builtins__": {}}, safe_dict)

        return f"计算结果: {expression} = {result}"

    except Exception as e:
        logger.error(f"计算错误: {e}")
        return f"计算失败: {str(e)}。请检查表达式是否正确。"


@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的天气状况（模拟数据）。

    Args:
        city: 城市名称，如 "北京", "上海", "深圳"

    Returns:
        天气信息
    """
    # 这里是模拟数据，实际应用中可以接入天气API
    weather_data = {
        "北京": "晴朗，气温 25°C，东南风 3级，空气质量良好",
        "上海": "多云，气温 28°C，东风 2级，湿度 65%",
        "深圳": "阴天，气温 30°C，南风 2级，有小雨",
        "广州": "雷阵雨，气温 29°C，西南风 4级",
        "成都": "多云，气温 23°C，无持续风向",
        "杭州": "晴，气温 27°C，东北风 2级",
    }

    result = weather_data.get(
        city,
        f"抱歉，暂无 {city} 的天气数据。当前支持的城市：{', '.join(weather_data.keys())}"
    )

    return f"{city}天气: {result}"


@tool
def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取当前时间。

    Args:
        timezone: 时区，默认为 "Asia/Shanghai"

    Returns:
        当前时间信息
    """
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(timezone)
        now = datetime.now(tz)

        return (
            f"当前时间:\n"
            f"  日期: {now.strftime('%Y年%m月%d日')}\n"
            f"  时间: {now.strftime('%H:%M:%S')}\n"
            f"  星期: {['一', '二', '三', '四', '五', '六', '日'][now.weekday()]}\n"
            f"  时区: {timezone}"
        )
    except Exception as e:
        # 降级方案
        now = datetime.now()
        return (
            f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"(注意: 使用系统本地时间)"
        )


@tool
def string_operations(operation: str, text: str, **kwargs) -> str:
    """
    执行字符串操作。

    Args:
        operation: 操作类型 (upper, lower, reverse, length, count)
        text: 要处理的文本
        **kwargs: 额外参数，如 count 操作需要 substring

    Returns:
        处理结果
    """
    try:
        if operation == "upper":
            return f"转大写: {text.upper()}"
        elif operation == "lower":
            return f"转小写: {text.lower()}"
        elif operation == "reverse":
            return f"反转: {text[::-1]}"
        elif operation == "length":
            return f"长度: {len(text)}"
        elif operation == "count":
            substring = kwargs.get("substring", "")
            if not substring:
                return "错误: count 操作需要提供 substring 参数"
            count = text.count(substring)
            return f"'{substring}' 在文本中出现 {count} 次"
        else:
            return (
                f"不支持的操作: {operation}\n"
                f"支持的操作: upper, lower, reverse, length, count"
            )
    except Exception as e:
        return f"字符串操作失败: {str(e)}"


@tool
def file_operations(operation: str, file_path: str, content: str = "") -> str:
    """
    执行文件操作（读取、写入、追加）。

    Args:
        operation: 操作类型 (read, write, append)
        file_path: 文件路径
        content: 要写入的内容（仅用于 write 和 append）

    Returns:
        操作结果
    """
    try:
        import os

        if operation == "read":
            if not os.path.exists(file_path):
                return f"文件不存在: {file_path}"

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return f"文件内容 ({file_path}):\n{content}"

        elif operation == "write":
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"成功写入文件: {file_path}"

        elif operation == "append":
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"成功追加到文件: {file_path}"

        else:
            return f"不支持的操作: {operation}"

    except Exception as e:
        logger.error(f"文件操作错误: {e}")
        return f"文件操作失败: {str(e)}"


# 导出所有工具
__all__ = [
    'calculator',
    'get_weather',
    'get_current_time',
    'string_operations',
    'file_operations'
]
