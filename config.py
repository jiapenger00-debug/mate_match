"""
应用配置 —— 统一管理环境变量和常量。
"""

import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 搜索相关
SEARCH_MAX_RESULTS = 5          # 每次搜索返回的最大条数
SEARCH_REQUEST_DELAY = 1.0      # 搜索请求间隔（秒），避免触发频率限制

# 视觉服务
VISION_BACKEND = os.getenv("VISION_BACKEND", "qwen_api")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-vl-max")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2-vl:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 服务
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
