# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**女性信息分析与匹配度计算工具** — 一个 Web 应用，用户可以输入女性的个人信息以及自己的信息，系统通过网络搜索补充数据，最终调用大模型 API（DeepSeek V4）计算两人匹配度并给出分析报告。

## 技术栈

- **后端**: Python 3.11+ / FastAPI / Uvicorn
- **前端**: Jinja2 模板 + 原生 CSS/JS（单文件 SPA 风格）
- **AI**: DeepSeek API（OpenAI 兼容接口）
- **搜索**: DuckDuckGo 即时搜索（ddgs 库）
- **配置**: python-dotenv 管理环境变量

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（命令行传入 Key，不落盘）
python main.py --api-key sk-DS密钥 --qwen-api-key sk-QW密钥

# Qwen Key 可选，不传则截图OCR/颜值评分不可用
python main.py --api-key sk-xxx --port 3000

# 生产部署（环境变量方式）
DEEPSEEK_API_KEY=sk-xxx QWEN_API_KEY=sk-xxx uvicorn main:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
├── main.py                    # FastAPI 入口，CLI 参数解析 + 路由定义
├── config.py                  # 环境变量 & 配置常量
├── models.py                  # Pydantic 请求/响应模型
├── services/
│   ├── __init__.py
│   ├── llm_service.py         # DeepSeek API 调用（分析匹配度）
│   └── search_service.py      # DuckDuckGo 网络搜索
├── templates/
│   ├── index.html             # 主页面（信息输入表单）
│   └── result.html            # 分析结果展示页
├── static/
│   └── style.css              # 全局样式
├── docs/
│   └── USAGE.md               # 详细使用指南
├── README.md                  # 代码架构文档
├── requirements.txt
└── .env.example               # 环境变量模板
```

## 核心数据流

1. 用户在 `index.html` 填写女方信息 + 自己的信息 → POST `/api/analyze`
2. `search_service.py` 对女方的关键信息执行网络搜索，获取公开资料补充
3. `llm_service.py` 组装 prompt（女方信息 + 搜索结果 + 用户信息），调用 DeepSeek API
4. LLM 返回结构化 JSON（匹配度总分 + 各维度分数 + 分析文字）
5. `result.html` 渲染分析报告

## 大模型调用

- 使用 OpenAI 兼容的 `/v1/chat/completions` 端点
- 通过 `response_format: { type: "json_object" }` 确保返回结构化 JSON
- 模型：`deepseek-chat`（DeepSeek V3/V4 系列）
- 匹配分析的 prompt 模板定义在 `llm_service.py` 的 `build_analysis_prompt()` 中

## API Key 传入方式（按优先级）

1. **命令行参数**（推荐）：`python main.py --api-key sk-xxx` — 密钥不落盘
2. **环境变量**：`DEEPSEEK_API_KEY=sk-xxx` — uvicorn 直接启动时使用
3. **`.env` 文件**：在项目根目录创建 `.env` — 需自行管理，已在 `.gitignore`

## 文档同步规则

每次修改代码后，根据变更类型判断是否需要同步文档：

| 变更类型 | 需更新 |
|----------|--------|
| 新增/删除路由、修改 API 接口 | `README.md`（架构图、路由说明）+ `USAGE.md`（使用示例） |
| 新增/修改 CLI 参数或配置项 | `README.md`（模块说明）+ `USAGE.md`（配置说明 + 启动命令） |
| 前端功能变更（如新增按钮、交互） | `README.md`（templates 部分） |
| 新增/修改 Docker 或部署方式 | `USAGE.md`（部署章节） |
| 仅改 CSS 样式、修 bug、重构 | 通常不需要，除非影响用户可见行为 |
| `services/llm_service.py` 中修改 prompt 或维度 | `USAGE.md`（分析维度说明） |

> 经验法则：如果用户手册（USAGE）或架构说明（README）会因此变得不准确，就必须更新。

## 注意事项

- `main.py` 启动时会解析 `--api-key` / `--host` / `--port`，这些参数优先级高于 `.env`
- DuckDuckGo 搜索有频率限制，`search_service.py` 中设置了请求间隔
- 生产环境部署建议配合 Nginx 反向代理 + HTTPS
