"""
Pydantic 数据模型 —— 定义 API 请求体和响应体。
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── 请求体 ──────────────────────────────────────────────

class GirlInfo(BaseModel):
    """女方的个人信息"""
    name: str = Field(..., description="姓名或昵称", min_length=1, max_length=50)
    age: Optional[int] = Field(None, ge=14, le=80, description="年龄")
    hometown: Optional[str] = Field(None, max_length=100, description="家乡")
    occupation: Optional[str] = Field(None, max_length=100, description="职业")
    edu_level: Optional[str] = Field(None, max_length=50, description="学历层次")
    edu_school: Optional[str] = Field(None, max_length=100, description="毕业院校")
    edu_tags: Optional[str] = Field(None, max_length=100, description="学校标签")
    personality: Optional[str] = Field(None, max_length=2000, description="性格描述")
    interests: Optional[str] = Field(None, max_length=2000, description="兴趣爱好")
    values: Optional[str] = Field(None, max_length=2000, description="价值观/人生追求")
    appearance: Optional[str] = Field(None, max_length=500, description="外貌特征")
    extra_info: Optional[str] = Field(None, max_length=2000, description="补充信息")


class UserInfo(BaseModel):
    """用户自己的个人信息"""
    name: str = Field(..., min_length=1, max_length=50, description="你的姓名或昵称")
    age: Optional[int] = Field(None, ge=14, le=80)
    hometown: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    edu_level: Optional[str] = Field(None, max_length=50, description="学历层次")
    edu_school: Optional[str] = Field(None, max_length=100, description="毕业院校")
    edu_tags: Optional[str] = Field(None, max_length=100, description="学校标签")
    personality: Optional[str] = Field(None, max_length=2000, description="性格描述")
    interests: Optional[str] = Field(None, max_length=2000)
    values: Optional[str] = Field(None, max_length=2000, description="价值观/人生追求")
    appearance: Optional[str] = Field(None, max_length=500)
    extra_info: Optional[str] = Field(None, max_length=2000)


class AnalyzeRequest(BaseModel):
    """匹配分析请求"""
    girl: GirlInfo
    user: UserInfo
    enable_search: bool = Field(True, description="是否启用网络搜索补充信息")


# ── 响应体 ──────────────────────────────────────────────

class DimensionScore(BaseModel):
    """单个维度的匹配分数"""
    dimension: str = Field(..., description="维度名称")
    score: int = Field(..., ge=0, le=100, description="该维度得分")
    comment: str = Field(..., description="该维度的简要分析")


class SearchResult(BaseModel):
    """网络搜索结果"""
    title: str
    url: str
    snippet: str


class AnalyzeResponse(BaseModel):
    """匹配分析响应"""
    overall_score: int = Field(..., ge=0, le=100, description="综合匹配度")
    dimensions: list[DimensionScore] = Field(..., description="各维度得分")
    summary: str = Field(..., description="综合评语")
    suggestion: str = Field(..., description="发展建议")
    search_results: Optional[list[SearchResult]] = Field(None, description="网络搜索结果")
