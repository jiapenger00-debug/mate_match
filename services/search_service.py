"""
网络搜索服务 —— 使用 Brave Search API 搜索公开信息以辅助分析。
免费额度 2000 次/月，国内直连，无需代理。
"""

import asyncio
import logging
import os
import ssl

import certifi
import httpx

from config import SEARCH_MAX_RESULTS
from models import SearchResult

logger = logging.getLogger(__name__)

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


async def search_girl_info(name: str, extra_keywords: str = "") -> list[SearchResult]:
    """
    搜索相关公开信息。

    Args:
        name: 姓名/昵称
        extra_keywords: 额外搜索关键词

    Returns:
        搜索结果列表（最多 SEARCH_MAX_RESULTS 条）
    """
    query = f"{name} {extra_keywords}".strip()
    if not query:
        return []

    if not BRAVE_API_KEY:
        logger.warning("未配置 BRAVE_API_KEY，跳过搜索")
        return []

    logger.info(f"Brave 搜索: {query}")

    try:
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        async with httpx.AsyncClient(timeout=5.0, verify=ssl_ctx) as client:
            resp = await client.get(
                BRAVE_API_URL,
                params={"q": query, "count": min(SEARCH_MAX_RESULTS, 20)},
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": BRAVE_API_KEY,
                },
            )
            if resp.status_code != 200:
                logger.warning(f"Brave 搜索失败: HTTP {resp.status_code}")
                return []
            data = resp.json()
            web = data.get("web", {}).get("results", [])
            results = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("description", ""),
                )
                for r in web
            ]
            logger.info(f"搜索完成，获取到 {len(results)} 条结果")
            return results
    except httpx.TimeoutException:
        logger.warning(f"Brave 搜索超时: {query}")
        return []
    except Exception as e:
        logger.warning(f"Brave 搜索失败: {e}")
        return []
