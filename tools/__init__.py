"""
工具模块初始化
集中导出所有可用工具
"""
from .basic_tools import (
    calculator,
    get_weather,
    get_current_time,
    string_operations,
    file_operations
)

from .search_tools import (
    search_web,
    search_news,
    search_with_tavily
)

from .rag_tools import (
    search_knowledge_base,
    add_documents_to_knowledge_base,
    rag_system
)

# 所有工具列表
ALL_TOOLS = [
    # 基础工具
    calculator,
    get_weather,
    get_current_time,
    string_operations,
    file_operations,

    # 搜索工具
    search_web,
    search_news,

    # RAG工具
    search_knowledge_base,
    add_documents_to_knowledge_base,
]

# 默认工具集（不包含需要额外配置的工具）
DEFAULT_TOOLS = [
    calculator,
    get_weather,
    get_current_time,
    search_web,
    search_knowledge_base,
]

__all__ = [
    'ALL_TOOLS',
    'DEFAULT_TOOLS',
    'calculator',
    'get_weather',
    'get_current_time',
    'string_operations',
    'file_operations',
    'search_web',
    'search_news',
    'search_with_tavily',
    'search_knowledge_base',
    'add_documents_to_knowledge_base',
    'rag_system'
]
