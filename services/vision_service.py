"""视觉服务 — 双后端（Qwen API / Ollama 本地）统一接口。"""

import base64
import json
import logging
import ssl

import certifi
import httpx
from openai import OpenAI

from config import VISION_BACKEND, QWEN_API_KEY, QWEN_MODEL, OLLAMA_MODEL, OLLAMA_BASE_URL

logger = logging.getLogger(__name__)


class VisionBackend:
    """视觉后端抽象基类（不使用 ABC 以避免依赖问题）。"""
    async def analyze(self, image_bytes: bytes, prompt: str) -> dict:
        raise NotImplementedError

    def supports_ocr(self) -> bool:
        return True


class QwenBackend(VisionBackend):
    """阿里云 DashScope（通义千问 VL）后端。"""
    def __init__(self):
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        http_client = httpx.Client(verify=ssl_ctx)
        self.client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            http_client=http_client,
        )

    async def analyze(self, image_bytes: bytes, prompt: str) -> dict:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"
        response = self.client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": prompt},
                ],
            }],
            max_tokens=1000,
            temperature=0.3,
        )
        raw = response.choices[0].message.content
        return _parse_json(raw)


class OllamaBackend(VisionBackend):
    """本地 Ollama 后端（qwen2-vl:7b）。"""
    async def analyze(self, image_bytes: bytes, prompt: str) -> dict:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "images": [b64],
                    "stream": False,
                    "format": "json",
                },
            )
            data = resp.json()
            return _parse_json(data.get("response", "{}"))


def get_backend() -> VisionBackend:
    """根据配置返回对应的视觉后端。"""
    if VISION_BACKEND == "local_ollama":
        logger.info(f"使用本地 Ollama 后端: {OLLAMA_MODEL}")
        return OllamaBackend()
    if VISION_BACKEND == "qwen_api" or VISION_BACKEND == "":
        if not QWEN_API_KEY:
            raise ValueError("未配置 QWEN_API_KEY，请在 .env 中设置或切换 VISION_BACKEND")
        logger.info(f"使用 Qwen API 后端: {QWEN_MODEL}")
        return QwenBackend()
    raise ValueError(f"未知 VISION_BACKEND: {VISION_BACKEND}")


def _parse_json(raw: str) -> dict:
    """从 LLM 返回文本中提取 JSON。"""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    import re
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    logger.warning(f"无法从视觉模型返回中解析 JSON: {raw[:200]}")
    return {}


async def analyze_beauty(image_bytes: bytes) -> dict:
    """分析人像照片的颜值。"""
    backend = get_backend()
    prompt = """先描述这张照片中人物的外貌特征，再进行客观的吸引力评估。返回 JSON（不要 markdown 包裹）：
{
  "description": "照片中人物的外貌描述：性别、大致年龄、发型发色、穿着风格、气质类型，50字以内",
  "score": 1到10的颜值分数（保留一位小数，5为平均，参考亚洲审美标准），
  "skin": "肤质评价（细腻/光滑/匀称/一般/粗糙）",
  "face_shape": "脸型（鹅蛋脸/瓜子脸/圆脸/方脸/长脸/心形脸）",
  "features": "五官特点简要描述，30字以内",
  "overall": "整体印象评价，20字以内"
}
如果照片中没有人脸，score 返回 0，overall 返回"未检测到人脸"，其余字段返回空字符串。
客观评价，不要刻意夸张或贬低。"""
    try:
        return await backend.analyze(image_bytes, prompt)
    except Exception as e:
        logger.error(f"颜值分析失败: {e}")
        return {"score": 0, "skin": "", "face_shape": "", "features": "", "overall": f"分析失败: {e}"}


async def analyze_supplement_photo(image_bytes: bytes) -> str:
    """分析补充照片，返回客观描述文本（非颜值评分）。"""
    backend = get_backend()
    prompt = """描述这张照片中的人物或场景。返回 JSON：
{
  "description": "客观描述照片内容：人物特征、穿着、场景、氛围等，50字以内。如果没有人脸，描述照片中的场景和信息"
}
只返回 JSON，不要其他文字。"""
    try:
        result = await backend.analyze(image_bytes, prompt)
        return result.get("description", "")
    except Exception as e:
        logger.error(f"补充照片分析失败: {e}")
        return ""


async def ocr_extract(image_bytes: bytes) -> dict:
    """从截图/照片中提取个人信息。"""
    backend = get_backend()
    prompt = """分析这张图片，提取其中提到的个人信息。返回 JSON（不要 markdown 包裹）：
{
  "name": "姓名（中文名或昵称）",
  "age": 年龄数字（整数），
  "hometown": "家乡/所在城市",
  "occupation": "职业",
  "edu_level": "学历（高中/中专/大专/本科/硕士/MBA/博士/博士后）",
  "edu_school": "毕业院校名称",
  "personality": "性格描述，50字以内",
  "interests": "兴趣爱好，50字以内",
  "values": "价值观或生活态度，50字以内",
  "appearance": "外貌特征描述，30字以内"
}
未提及的字段返回 null，不要猜测或编造。只返回 JSON，不要其他文字。"""
    try:
        return await backend.analyze(image_bytes, prompt)
    except Exception as e:
        logger.error(f"截图解析失败: {e}")
        return {}


async def analyze_beauty_pair(girl_bytes: bytes, user_bytes: bytes) -> dict:
    """分析双方照片，返回各自评分 + 颜值匹配度。"""
    import asyncio
    girl_result, user_result = await asyncio.gather(
        analyze_beauty(girl_bytes),
        analyze_beauty(user_bytes),
    )
    gs = girl_result.get("score", 0)
    us = user_result.get("score", 0)
    if gs > 0 and us > 0:
        gap = abs(gs - us)
        match = max(0, 100 - int(gap * 15))
        if gap <= 0.5:
            comment = "天作之合，颜值非常登对！"
        elif gap <= 1.5:
            comment = "颜值匹配度较高，很般配"
        elif gap <= 2.5:
            comment = "颜值有一定差距，但互补也是魅力"
        else:
            comment = "颜值差异较大，不过真爱不看脸"
    else:
        match = 0
        comment = "未能完整分析双方照片"
    return {
        "girl": girl_result,
        "user": user_result,
        "beauty_match": match,
        "beauty_comment": comment,
    }
