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

# 服务
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
