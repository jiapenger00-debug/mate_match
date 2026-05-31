# 灵魂契合度分析

> 💘 输入两人信息，AI 综合分析匹配程度 — Web 应用

基于 **Python + FastAPI + DeepSeek 大模型** 构建的匹配度分析工具。输入女方的个人信息以及用户自己的信息，系统可选择性地通过网络搜索补充数据，最终调用大模型 API 从多维度计算两人契合度，并生成可视化分析报告。

---

## 快速启动

```bash
pip install -r requirements.txt
python main.py --api-key sk-你的密钥
```

浏览器打开 `http://localhost:8000`

> 密钥通过命令行传入，不落盘。也可以用环境变量或 `.env` 文件，详见 [docs/USAGE.md](docs/USAGE.md)。

> 📖 详细使用说明请参阅 [docs/USAGE.md](docs/USAGE.md)

---

## 代码架构

### 整体架构

```
┌──────────────────────────────────────────────────┐
│                  浏览器 (Jinja2 模板)              │
│         index.html ←→ result.html                │
└──────────────────────┬───────────────────────────┘
                       │ HTTP (Form POST)
                       ▼
┌──────────────────────────────────────────────────┐
│               main.py  (FastAPI 路由层)           │
│  GET  /              → 渲染输入表单               │
│  POST /api/analyze   → 搜索 → LLM分析 → 结果页    │
└───────┬──────────────────────────────┬───────────┘
        │                              │
        ▼                              ▼
┌───────────────┐            ┌────────────────────┐
│ search_service│            │   llm_service       │
│ (DuckDuckGo)  │            │ (DeepSeek API)      │
│               │            │                     │
│ 搜索女方公开   │            │ System Prompt        │
│ 信息作为 LLM  │──Refs──▶  │ + 用户消息           │
│ 分析的补充参考 │            │ → JSON 结构化返回    │
└───────────────┘            └────────────────────┘
        │                              │
        └──────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│              models.py  (数据层)                  │
│  GirlInfo / UserInfo / AnalyzeResponse / ...     │
│  所有请求体和响应体通过 Pydantic 严格校验          │
└──────────────────────────────────────────────────┘
```

### 调用时序

```
用户提交表单
    │
    ▼
main.py: POST /api/analyze
    │
    ├─ ① 解析 Form 数据 → 构建 GirlInfo + UserInfo (Pydantic 校验)
    │
    ├─ ② (可选) search_service.search_girl_info(name, keywords)
    │      └─ asyncio.to_thread → DDGS.text()  最多 5 条结果
    │
    ├─ ③ llm_service.analyze_matching(girl, user, search_results)
    │      ├─ build_user_message()  组装 Markdown 格式 prompt
    │      ├─ OpenAI client.chat.completions.create()
    │      │    model: deepseek-chat
    │      │    response_format: json_object
    │      │    temperature: 0.7
    │      │    max_tokens: 2000
    │      └─ json.loads() → AnalyzeResponse (Pydantic 校验)
    │
    └─ ④ 渲染 result.html → 返回 HTML
```

---

## 文件结构

```
vibe_coding_tutorial/
│
├── main.py                       # [入口] FastAPI 应用、路由、启动配置
├── config.py                     # [配置] 环境变量读取、全局常量
├── models.py                     # [模型] Pydantic 请求/响应数据结构
├── requirements.txt              # [依赖] Python 包列表
├── .env.example                  # [模板] 环境变量示例
├── .gitignore
│
├── services/                     # [服务层] 核心业务逻辑
│   ├── __init__.py               #   公开导出 search_girl_info, analyze_matching, save_share, get_share
│   ├── search_service.py         #   DuckDuckGo 网络搜索
│   ├── llm_service.py            #   DeepSeek API 调用 + Prompt 构建
│   └── share_service.py          #   分享数据持久化（SQLite）
│
├── templates/                    # [视图层] Jinja2 模板
│   ├── index.html                #   信息输入表单（女方 + 用户）
│   ├── result.html               #   分析报告展示（分数/维度/建议/分享栏）
│   └── share.html                #   分享名片页（精简卡片 + 可展开完整报告）
│
├── static/                       # [静态资源]
│   ├── style.css                 #   全局样式（双主题 + 搜索/分享/示例选择器）
│   └── demo-data.js              #   4 组示例情侣数据
│
├── docs/                         # [文档]
│   └── USAGE.md                  #   详细使用指南
```

---

## 模块职责

### `main.py` — 应用入口 + 路由层

| 路由 | 方法 | 职责 |
|------|------|------|
| `/` | GET | 渲染 `index.html` 表单页面 |
| `/api/analyze` | POST | 接收 Form 数据，串联搜索 → LLM 分析，渲染 `result.html`，自动生成分享链接 |
| `/api/search` | POST | 仅执行搜索，返回 JSON 结果列表（前端异步展示） |
| `/api/share` | POST | 接收 JSON 分析结果，存入 SQLite，返回短 ID |
| `/s/<id>` | GET | 渲染分享名片页（精简卡片 + 可展开完整报告） |

核心逻辑：
- 启动时解析 `--api-key` / `--host` / `--port` 命令行参数，设置环境变量后再导入其他模块
- `_parse_int()` — 将表单字符串安全转为 `int`，空值返回 `None`
- API Key 缺失时返回友好错误页面，引导用户配置
- 异常捕获：LLM 调用失败时返回降级结果而非 500 错误
- `/api/analyze` 支持 `selected_results` 参数，前端可传入预筛选结果跳过搜索

### `config.py` — 配置层

通过 `python-dotenv` 加载 `.env` 文件，集中管理：
- DeepSeek API 的连接参数（Key / URL / Model）
- 搜索引擎参数（结果上限 / 请求间隔）
- 服务器监听参数（Host / Port）

> 命令行参数 `--api-key` / `--host` / `--port` 优先级高于 `.env` 文件。

### `models.py` — 数据层

| 模型 | 类型 | 用途 |
|------|------|------|
| `GirlInfo` | 请求 | 女方的个人信息（11 字段，name 必填） |
| `UserInfo` | 请求 | 用户的个人信息（11 字段，name 必填） |
| `AnalyzeRequest` | 请求 | 完整分析请求（含 girl + user + 搜索开关） |
| `DimensionScore` | 响应 | 单维度得分（维度名 + 分数 + 评语） |
| `SearchResult` | 响应 | 网络搜索结果（标题 + URL + 摘要） |
| `AnalyzeResponse` | 响应 | 完整分析结果（总分 + 维度列表 + 评语 + 建议） |

所有字段通过 Pydantic `Field` 设置了约束（`min_length` / `ge` / `le` / `max_length`），前端表单也做了对应的 `required` / `min` / `max` 验证。

### `services/search_service.py` — 搜索服务

- **对外接口**：`search_girl_info(name, extra_keywords) -> list[SearchResult]`
- **搜索引擎**：DuckDuckGo（通过 `ddgs` Python 库）
- **异步策略**：`ddgs` 是同步库，通过 `asyncio.to_thread()` 放入线程池执行，避免阻塞 FastAPI 事件循环
- **容错**：搜索失败返回空列表，不中断主流程

### `services/llm_service.py` — 大模型服务

- **对外接口**：`analyze_matching(girl, user, search_results) -> AnalyzeResponse`
- **LLM 调用**：使用 OpenAI 兼容 SDK 连接 DeepSeek API
- **Prompt 设计**：
  - `SYSTEM_PROMPT` — 定义 LLM 角色、分析原则、输出格式
  - `build_user_message()` — 将 GirlInfo + UserInfo + SearchResult 组装为结构化 Markdown 文本
- **结构化输出**：`response_format: {"type": "json_object"}` 确保返回合法 JSON
- **JSON 解析容错**：`json.JSONDecodeError` 时返回降级结果（score=0, 提示重试）
- **可替换性**：修改 `config.py` 中的 Base URL 和 Model 即可切换为其他兼容 OpenAI 接口的模型

### `templates/` — 视图层

- **index.html** — 表单页面，CSS Grid 双列布局；内置**标签式示例选择器**（4 组情侣模板，点击预览后确认填充）；异步搜索流程（搜索动画 → 结果卡片勾选 → AI 分析）；右上角**明暗主题切换按钮**
- **result.html** — 报告页面，通过 Jinja2 模板语法渲染；底部**分享栏**（复制链接 + toast 提示），支持生成公开分享页
- **share.html** — 分享名片页：精简卡片（两人名字 + 匹配度圆环 + 等级 + 评语）+ 可展开完整报告

### `static/style.css` — 样式

- CSS 变量双主题设计：`[data-theme="dark"]`（暗夜浪漫）和 `[data-theme="light"]`（日暖浪漫），通过 `data-theme` 属性切换
- Noto Serif SC 衬线标题字体 + Google Fonts 加载
- 浮动花瓣粒子动画（10 个 CSS 随机轨迹）
- 卡片渐入动画（staggered fadeInUp）
- 搜索增强：全屏覆盖层动画 + 进度条 + 结果卡片
- 示例选择器：标签栏 + 预览面板 + 确认/取消按钮
- 分享栏：URL 输入框 + 复制按钮 + toast 提示
- 响应式布局 + `prefers-reduced-motion` 降级

---

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.11+ | 运行语言 |
| [FastAPI](https://fastapi.tiangolo.com/) | Web 框架 |
| [Uvicorn](https://www.uvicorn.org/) | ASGI 服务器 |
| [Jinja2](https://jinja.palletsprojects.com/) | 模板引擎（服务端渲染） |
| [Pydantic](https://docs.pydantic.dev/) | 数据校验与序列化 |
| [OpenAI SDK](https://github.com/openai/openai-python) | 调用 DeepSeek API（OpenAI 兼容） |
| [ddgs](https://pypi.org/project/ddgs/) | DuckDuckGo 搜索 |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 环境变量管理 |

---

## 扩展指南

### 添加新的分析维度

编辑 `services/llm_service.py`，修改 `SYSTEM_PROMPT` 中的 `dimensions` 数组，例如增加「经济观念契合度」：

```json
{"dimension": "经济观念契合度", "score": 72, "comment": "..."}
```

### 切换其他 LLM

编辑 `.env`：

```env
DEEPSEEK_BASE_URL=https://api.openai.com/v1
DEEPSEEK_MODEL=gpt-4o
DEEPSEEK_API_KEY=sk-xxx
```

任何兼容 OpenAI `/v1/chat/completions` 接口的服务都可以直接替换。

### 添加数据库持久化

1. 创建数据库模型（SQLAlchemy / SQLModel）
2. 在 `main.py` 的 `/api/analyze` 中保存分析记录
3. 新增 `/history` 路由查看历史分析
