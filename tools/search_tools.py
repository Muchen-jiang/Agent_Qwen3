"""
网络搜索工具
支持多种搜索引擎: DuckDuckGo, Tavily, Serper等
"""
from typing import List, Dict, Optional
from langchain_core.tools import tool
from config import search_config
import logging

logger = logging.getLogger(__name__)


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    在互联网上搜索信息。

    Args:
        query: 搜索查询字符串
        max_results: 返回的最大结果数，默认为5

    Returns:
        搜索结果的文本摘要
    """
    try:
        # 使用DuckDuckGo搜索（免费，无需API key）
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(
                query,
                max_results=min(max_results, search_config.MAX_RESULTS)
            ))

            for idx, result in enumerate(search_results, 1):
                title = result.get('title', 'No title')
                snippet = result.get('body', 'No description')
                url = result.get('href', 'No URL')

                results.append(
                    f"{idx}. **{title}**\n"
                    f"   {snippet}\n"
                    f"   来源: {url}\n"
                )

        if not results:
            return f"没有找到关于 '{query}' 的搜索结果。"

        return (
            f"关于 '{query}' 的搜索结果:\n\n" +
            "\n".join(results)
        )

    except ImportError:
        return (
            "错误: 缺少 duckduckgo-search 库。"
            "请运行: pip install duckduckgo-search"
        )
    except Exception as e:
        logger.error(f"搜索错误: {e}")
        return f"搜索时发生错误: {str(e)}"


@tool
def search_news(query: str, max_results: int = 3) -> str:
    """
    搜索最新的新闻资讯。

    Args:
        query: 搜索查询字符串
        max_results: 返回的最大结果数，默认为3

    Returns:
        新闻搜索结果
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            news_results = list(ddgs.news(
                query,
                max_results=min(max_results, search_config.MAX_RESULTS)
            ))

            for idx, result in enumerate(news_results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                url = result.get('url', 'No URL')
                date = result.get('date', 'Unknown date')

                results.append(
                    f"{idx}. **{title}**\n"
                    f"   时间: {date}\n"
                    f"   {body}\n"
                    f"   来源: {url}\n"
                )

        if not results:
            return f"没有找到关于 '{query}' 的新闻。"

        return (
            f"关于 '{query}' 的最新新闻:\n\n" +
            "\n".join(results)
        )

    except ImportError:
        return "错误: 缺少 duckduckgo-search 库"
    except Exception as e:
        logger.error(f"新闻搜索错误: {e}")
        return f"搜索新闻时发生错误: {str(e)}"


# 可选：如果有API key，可以使用Tavily搜索
@tool
def search_with_tavily(query: str) -> str:
    """
    使用Tavily进行高质量搜索（需要API key）。

    Args:
        query: 搜索查询字符串

    Returns:
        Tavily搜索结果
    """
    if not search_config.TAVILY_API_KEY:
        return "错误: 未配置 TAVILY_API_KEY"

    try:
        from langchain_community.tools.tavily_search import TavilySearchResults

        tavily_tool = TavilySearchResults(
            api_key=search_config.TAVILY_API_KEY,
            max_results=search_config.MAX_RESULTS
        )

        results = tavily_tool.invoke({"query": query})

        formatted_results = []
        for idx, result in enumerate(results, 1):
            formatted_results.append(
                f"{idx}. {result.get('title', 'No title')}\n"
                f"   {result.get('content', 'No content')}\n"
                f"   来源: {result.get('url', 'No URL')}\n"
            )

        return (
            f"关于 '{query}' 的高质量搜索结果:\n\n" +
            "\n".join(formatted_results)
        )

    except Exception as e:
        logger.error(f"Tavily搜索错误: {e}")
        return f"Tavily搜索时发生错误: {str(e)}"


# 导出所有工具
__all__ = ['search_web', 'search_news', 'search_with_tavily']
