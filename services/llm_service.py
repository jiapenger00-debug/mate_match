"""
DeepSeek 大模型服务 —— 调用大模型进行匹配度分析。
"""

import json
import logging
import ssl

import certifi
import httpx
from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from models import GirlInfo, UserInfo, AnalyzeResponse, DimensionScore, SearchResult

logger = logging.getLogger(__name__)

# 核心分析 System Prompt
SYSTEM_PROMPT = """你是一位专业的感情分析与匹配度评估专家。用户会提供两个人的个人信息，
你需要从多个维度全面分析两人的匹配程度，并给出客观、有建设性的评估报告。

分析时请遵循以下原则：
1. **客观中立**：基于事实信息分析，不做主观臆断
2. **多维度考量**：从性格、价值观、兴趣爱好、生活方式、成长背景等多个角度评估
3. **建设性**：不只给出分数，更要指出契合点和潜在差异点
4. **尊重隐私**：不对任何一方做负面评判，保持尊重
5. **分数合理**：60分以下表示差异较大，60-75表示有一定基础，75-85表示比较匹配，85以上表示高度契合

请务必以 JSON 格式返回结果，格式如下：
{
  "overall_score": 78,
  "dimensions": [
    {"dimension": "性格契合度", "score": 80, "comment": "..."},
    {"dimension": "价值观契合度", "score": 75, "comment": "..."},
    {"dimension": "兴趣爱好契合度", "score": 70, "comment": "..."},
    {"dimension": "生活方式契合度", "score": 82, "comment": "..."},
    {"dimension": "成长背景契合度", "score": 85, "comment": "..."}
  ],
  "summary": "综合评语，100-200字",
  "suggestion": "发展建议，100-200字"
}
"""


def build_user_message(
    girl: GirlInfo,
    user: UserInfo,
    search_results: list[SearchResult] | None = None,
    user_search_results: list[SearchResult] | None = None,
) -> str:
    """构建发送给 LLM 的用户消息"""

    parts: list[str] = ["## 女方信息"]

    # 女方基本信息
    parts.append(f"- 姓名/昵称：{girl.name}")
    if girl.age is not None:
        parts.append(f"- 年龄：{girl.age}")
    if girl.hometown:
        parts.append(f"- 家乡：{girl.hometown}")
    if girl.occupation:
        parts.append(f"- 职业：{girl.occupation}")
    if girl.edu_level or girl.edu_school:
        edu_parts = []
        if girl.edu_level:
            edu_parts.append(girl.edu_level)
        if girl.edu_school:
            school_str = girl.edu_school
            if girl.edu_tags:
                school_str += f"（{girl.edu_tags.replace(',', '/')}）"
            edu_parts.append(school_str)
        parts.append(f"- 学历/学校：{'，'.join(edu_parts)}")
    if girl.appearance:
        parts.append(f"- 外貌特征：{girl.appearance}")
    if girl.personality:
        parts.append(f"- 性格描述：{girl.personality}")
    if girl.interests:
        parts.append(f"- 兴趣爱好：{girl.interests}")
    if girl.values:
        parts.append(f"- 价值观/人生追求：{girl.values}")
    if girl.extra_info:
        parts.append(f"- 补充信息：{girl.extra_info}")
    if girl.requirements:
        parts.append(f"- 对对方的要求：{girl.requirements}")

    # 搜索结果补充
    if search_results:
        parts.append("\n### 女方公开信息参考")
        for i, sr in enumerate(search_results, 1):
            parts.append(f"{i}. {sr.title}\n   {sr.snippet}")
    if user_search_results:
        parts.append("\n### 男方公开信息参考")
        for i, sr in enumerate(user_search_results, 1):
            parts.append(f"{i}. {sr.title}\n   {sr.snippet}")

    # 用户信息
    parts.append("\n## 用户（男方）信息")
    parts.append(f"- 姓名/昵称：{user.name}")
    if user.age is not None:
        parts.append(f"- 年龄：{user.age}")
    if user.hometown:
        parts.append(f"- 家乡：{user.hometown}")
    if user.occupation:
        parts.append(f"- 职业：{user.occupation}")
    if user.edu_level or user.edu_school:
        edu_parts = []
        if user.edu_level:
            edu_parts.append(user.edu_level)
        if user.edu_school:
            school_str = user.edu_school
            if user.edu_tags:
                school_str += f"（{user.edu_tags.replace(',', '/')}）"
            edu_parts.append(school_str)
        parts.append(f"- 学历/学校：{'，'.join(edu_parts)}")
    if user.appearance:
        parts.append(f"- 外貌特征：{user.appearance}")
    if user.personality:
        parts.append(f"- 性格描述：{user.personality}")
    if user.interests:
        parts.append(f"- 兴趣爱好：{user.interests}")
    if user.values:
        parts.append(f"- 价值观/人生追求：{user.values}")
    if user.extra_info:
        parts.append(f"- 补充信息：{user.extra_info}")
    if user.requirements:
        parts.append(f"- 对对方的要求：{user.requirements}")

    parts.append("\n请基于以上信息，综合分析两人的匹配程度。")
    return "\n".join(parts)


async def analyze_matching(
    girl: GirlInfo,
    user: UserInfo,
    search_results: list[SearchResult] | None = None,
    user_search_results: list[SearchResult] | None = None,
) -> AnalyzeResponse:
    """
    调用 DeepSeek API 进行匹配度分析。

    Args:
        girl: 女方信息
        user: 用户信息
        search_results: 网络搜索结果

    Returns:
        AnalyzeResponse: 匹配分析结果
    """
    # 使用 certifi 证书包，避免 Windows 上 SSL_CERT_FILE 环境变量指向无效路径
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.Client(verify=ssl_context)
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        http_client=http_client,
    )

    user_message = build_user_message(girl, user, search_results, user_search_results)

    logger.info(f"调用 {DEEPSEEK_MODEL} 进行匹配分析...")
    logger.debug(f"Prompt 长度: {len(user_message)} 字符")

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=2000,
    )

    raw_text = response.choices[0].message.content
    logger.debug(f"LLM 原始返回: {raw_text}")

    # 解析 JSON 返回
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error(f"LLM 返回的 JSON 解析失败: {raw_text}")
        # 返回一个降级结果
        return AnalyzeResponse(
            overall_score=0,
            dimensions=[],
            summary="分析失败，请稍后重试。",
            suggestion="",
            search_results=search_results,
        )

    # 构建响应对象
    dimensions = [
        DimensionScore(
            dimension=d["dimension"],
            score=d["score"],
            comment=d["comment"],
        )
        for d in data.get("dimensions", [])
    ]

    return AnalyzeResponse(
        overall_score=data.get("overall_score", 0),
        dimensions=dimensions,
        summary=data.get("summary", ""),
        suggestion=data.get("suggestion", ""),
        search_results=search_results,
    )
