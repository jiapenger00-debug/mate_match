"""
网络搜索服务 —— 使用 DuckDuckGo 搜索公开信息以辅助分析。
"""

import asyncio
import logging
from ddgs import DDGS

from config import SEARCH_MAX_RESULTS
from models import SearchResult

logger = logging.getLogger(__name__)


async def search_girl_info(name: str, extra_keywords: str = "") -> list[SearchResult]:
    """
    搜索女方的相关公开信息。

    Args:
        name: 女方姓名/昵称
        extra_keywords: 额外搜索关键词（如职业、学校等）

    Returns:
        搜索结果列表（最多 SEARCH_MAX_RESULTS 条）
    """
    query = f"{name} {extra_keywords}".strip()
    if not query:
        return []

    logger.info(f"执行网络搜索: {query}")

    try:
        # ddgs 是同步库，在线程池中运行避免阻塞事件循环
        raw_results = await asyncio.to_thread(
            _ddgs_search, query, max_results=SEARCH_MAX_RESULTS
        )
        logger.info(f"搜索完成，获取到 {len(raw_results)} 条结果")
        return raw_results
    except Exception as e:
        logger.warning(f"搜索失败: {e}")
        return []


def _ddgs_search(query: str, max_results: int) -> list[SearchResult]:
    """同步的 DDGS 搜索（在 asyncio.to_thread 中执行）"""
    results: list[SearchResult] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("href", ""),
                snippet=item.get("body", ""),
            ))
    return results
