"""
FastAPI 主入口 —— 灵魂契合度分析 Web 应用。

启动方式:
    python main.py --api-key sk-xxx --qwen-api-key sk-xxx     # 两个 Key 都通过命令行传入
    python main.py --api-key sk-xxx --port 3000               # 只用 DeepSeek
    uvicorn main:app --reload --host 0.0.0.0 --port 8000     # 需先配 .env
"""

import os
import sys

# ── 命令行参数解析（必须在导入项目模块之前）───────────
# 支持: python main.py --api-key sk-xxx --qwen-api-key sk-xxx [--host 0.0.0.0] [--port 8000]
_cli_keys = {"--api-key", "--qwen-api-key", "--brave-api-key", "--host", "--port"}
_args = sys.argv[1:]
for i, arg in enumerate(_args):
    if arg == "--api-key" and i + 1 < len(_args):
        os.environ["DEEPSEEK_API_KEY"] = _args[i + 1]
    elif arg == "--qwen-api-key" and i + 1 < len(_args):
        os.environ["QWEN_API_KEY"] = _args[i + 1]
    elif arg == "--host" and i + 1 < len(_args):
        os.environ["HOST"] = _args[i + 1]
    elif arg == "--port" and i + 1 < len(_args):
        os.environ["PORT"] = _args[i + 1]

import logging
from pathlib import Path

from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import HOST, PORT, DEEPSEEK_API_KEY
from models import GirlInfo, UserInfo, AnalyzeResponse, SearchResult
from services import search_girl_info, analyze_matching, save_share, get_share

# 颜值分析结果暂存（后台线程写入，轮询端点读取）
_beauty_cache: dict[str, dict | None] = {}

# ── 日志 ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── 应用初始化 ────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="灵魂契合度分析",
    description="输入两人信息，AI 综合分析匹配程度",
    version="1.0.0",
)

# 静态文件 & 模板
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ── 工具函数 ──────────────────────────────────────────

def _parse_int(value: str | None) -> int | None:
    """安全地将字符串转为 int，失败返回 None"""
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


# ── 路由 ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页：信息输入表单"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/search")
async def search_only(
    girl_name: str = Form(""),
    girl_hometown: str = Form(""),
    girl_occupation: str = Form(""),
    girl_edu_level: str = Form(""),
    girl_edu_school: str = Form(""),
):
    """仅执行搜索，返回结果列表 JSON，不调用 LLM。"""
    name = girl_name.strip()
    extra_kw = " ".join(filter(None, [girl_occupation, girl_edu_level, girl_edu_school, girl_hometown]))
    results = await search_girl_info(name, extra_kw)
    import json as _json
    return HTMLResponse(
        content=_json.dumps(
            [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in results],
            ensure_ascii=False
        ),
        media_type="application/json"
    )


@app.post("/api/ocr")
async def ocr_import(request: Request):
    """接收截图/照片，用多模态 LLM 提取个人信息。"""
    from services.vision_service import ocr_extract

    form = await request.form()
    image_file = form.get("image")
    if not image_file:
        return HTMLResponse(
            content='{"error": "未上传图片"}',
            status_code=400, media_type="application/json"
        )

    try:
        image_bytes = await image_file.read()
        result = await ocr_extract(image_bytes)
        import json as _json
        return HTMLResponse(
            content=_json.dumps(result, ensure_ascii=False),
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"OCR 解析失败: {e}")
        return HTMLResponse(
            content='{"error": "' + str(e) + '"}',
            status_code=500, media_type="application/json"
        )


@app.get("/beauty", response_class=HTMLResponse)
async def beauty_page(request: Request):
    """颜值 PK 页面。"""
    return templates.TemplateResponse("beauty.html", {"request": request})


@app.post("/api/beauty/single")
async def analyze_beauty_single(request: Request):
    """接收单张照片，返回颜值评分。"""
    from services.vision_service import analyze_beauty
    import json as _json

    form = await request.form()
    photo = form.get("photo")
    if not photo:
        return HTMLResponse(content='{"error":"请上传照片"}', status_code=400, media_type="application/json")
    try:
        img_bytes = await photo.read()
        result = await analyze_beauty(img_bytes)
        return HTMLResponse(content=_json.dumps(result, ensure_ascii=False), media_type="application/json")
    except Exception as e:
        return HTMLResponse(content='{"error":"' + str(e) + '"}', status_code=500, media_type="application/json")


@app.post("/api/beauty")
async def analyze_beauty_api(request: Request):
    """接收双方照片，返回颜值评分。"""
    from services.vision_service import analyze_beauty_pair

    form = await request.form()
    girl_file = form.get("girl_photo")
    user_file = form.get("user_photo")

    if not girl_file or not user_file:
        return HTMLResponse(
            content='{"error": "请上传双方照片"}',
            status_code=400, media_type="application/json"
        )

    try:
        girl_bytes = await girl_file.read()
        user_bytes = await user_file.read()
        result = await analyze_beauty_pair(girl_bytes, user_bytes)
        import json as _json
        return HTMLResponse(
            content=_json.dumps(result, ensure_ascii=False),
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"颜值分析失败: {e}")
        import json as _json
        return HTMLResponse(
            content=_json.dumps({"error": str(e)}, ensure_ascii=False),
            status_code=500, media_type="application/json"
        )


@app.post("/api/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    # ── 女方信息 ──
    girl_name: str = Form(...),
    girl_age: str = Form(""),
    girl_hometown: str = Form(""),
    girl_occupation: str = Form(""),
    girl_edu_level: str = Form(""),
    girl_edu_school: str = Form(""),
    girl_edu_tags: str = Form(""),
    girl_appearance: str = Form(""),
    girl_personality: str = Form(""),
    girl_interests: str = Form(""),
    girl_values: str = Form(""),
    girl_extra: str = Form(""),
    girl_requirements: str = Form(""),
    # ── 用户信息 ──
    user_name: str = Form(...),
    user_age: str = Form(""),
    user_hometown: str = Form(""),
    user_occupation: str = Form(""),
    user_edu_level: str = Form(""),
    user_edu_school: str = Form(""),
    user_edu_tags: str = Form(""),
    user_appearance: str = Form(""),
    user_personality: str = Form(""),
    user_interests: str = Form(""),
    user_values: str = Form(""),
    user_extra: str = Form(""),
    user_requirements: str = Form(""),
    # ── 选项 ──
    enable_search_girl: bool = Form(True),
    enable_search_user: bool = Form(True),
    selected_results: str = Form(""),
    selected_results_user: str = Form(""),
    girl_photo: UploadFile | None = File(None),
    user_photo: UploadFile | None = File(None),
):
    """核心分析接口：接收表单数据，执行搜索 + LLM 分析，返回结果页"""

    # 构建 Pydantic 模型
    girl = GirlInfo(
        name=girl_name.strip(),
        age=_parse_int(girl_age),
        hometown=girl_hometown.strip() or None,
        occupation=girl_occupation.strip() or None,
        edu_level=girl_edu_level.strip() or None,
        edu_school=girl_edu_school.strip() or None,
        edu_tags=girl_edu_tags.strip() or None,
        appearance=girl_appearance.strip() or None,
        personality=girl_personality.strip() or None,
        interests=girl_interests.strip() or None,
        values=girl_values.strip() or None,
        extra_info=girl_extra.strip() or None,
        requirements=girl_requirements.strip() or None,
    )

    user = UserInfo(
        name=user_name.strip(),
        age=_parse_int(user_age),
        hometown=user_hometown.strip() or None,
        occupation=user_occupation.strip() or None,
        edu_level=user_edu_level.strip() or None,
        edu_school=user_edu_school.strip() or None,
        edu_tags=user_edu_tags.strip() or None,
        appearance=user_appearance.strip() or None,
        personality=user_personality.strip() or None,
        interests=user_interests.strip() or None,
        values=user_values.strip() or None,
        extra_info=user_extra.strip() or None,
        requirements=user_requirements.strip() or None,
    )

    logger.info(f"收到分析请求: {girl.name} × {user.name}, 搜索女方={enable_search_girl} 男方={enable_search_user}")

    # 检查 API Key
    if not DEEPSEEK_API_KEY:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "girl_name": girl.name,
            "user_name": user.name,
            "overall_score": 0,
            "dimensions": [],
            "summary": "未配置 DeepSeek API Key，无法进行分析。请通过 --api-key 参数传入密钥，或创建 .env 文件。",
            "suggestion": "获取免费 Key: https://platform.deepseek.com",
            "search_results": [],
        })

    # 步骤1：网络搜索（可选，并行执行双方搜索）
    import json as _json
    import asyncio as _asyncio
    search_results = None
    user_search_results = None

    async def _search_girl():
        if not enable_search_girl: return None
        if selected_results:
            try:
                raw = _json.loads(selected_results)
                return [SearchResult(title=r["title"], url=r.get("url",""), snippet=r["snippet"]) for r in raw]
            except Exception: pass
            return None
        kw = " ".join(filter(None, [girl.occupation, girl.edu_level, girl.edu_school, girl.hometown]))
        return await search_girl_info(girl.name, kw)

    async def _search_user():
        if not enable_search_user: return None
        if selected_results_user:
            try:
                raw = _json.loads(selected_results_user)
                return [SearchResult(title=r["title"], url=r.get("url",""), snippet=r["snippet"]) for r in raw]
            except Exception: pass
            return None
        kw = " ".join(filter(None, [user.occupation, user.edu_level, user.edu_school, user.hometown]))
        return await search_girl_info(user.name, kw)

    search_results, user_search_results = await _asyncio.gather(_search_girl(), _search_user())
    logger.info(f"搜索到 女方{len(search_results or [])} + 男方{len(user_search_results or [])} 条结果")

    # 提前生成 beauty_id（用于后续异步更新颜值结果）
    import secrets as _secrets
    import threading as _threading
    beauty_sid = _secrets.token_urlsafe(4).replace("-","").replace("_","")[:6]
    _beauty_cache[beauty_sid] = None  # None = 还在分析中

    # 颜值分析后台线程运行
    if girl_photo or user_photo:
        from services.vision_service import analyze_beauty_pair as _beauty
        def _do_beauty_sync(sid):
            try:
                gb = girl_photo.file.read() if girl_photo else None
                ub = user_photo.file.read() if user_photo else None
                if gb and ub:
                    loop = _asyncio.new_event_loop()
                    _asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(_beauty(gb, ub))
                    loop.close()
                    _beauty_cache[sid] = result
            except Exception:
                _beauty_cache[sid] = {"error": True}
        _threading.Thread(target=_do_beauty_sync, args=(beauty_sid,), daemon=True).start()

    async def _do_llm():
        try:
            return await analyze_matching(girl, user, search_results, user_search_results)
        except Exception as e:
            logger.error(f"LLM 分析失败: {e}", exc_info=True)
            return AnalyzeResponse(overall_score=0, dimensions=[], summary=f"分析服务暂时不可用，请稍后重试。错误信息：{e}", suggestion="请检查 API Key 是否正确配置，或网络连接是否正常。", search_results=search_results)
    result = await _do_llm()

    # 步骤3：保存分享数据
    share_id = None
    try:
        share_data = {
            "girl_name": girl.name,
            "user_name": user.name,
            "overall_score": result.overall_score,
            "dimensions": [d.model_dump() for d in result.dimensions],
            "summary": result.summary,
            "suggestion": result.suggestion,
            "search_results": [sr.model_dump() for sr in (result.search_results or [])],
        }
        share_id = save_share(share_data)
        logger.info(f"分享链接已创建: /s/{share_id}")
    except Exception as e:
        logger.warning(f"保存分享数据失败: {e}")

    # 渲染结果页
    return templates.TemplateResponse("result.html", {
        "request": request,
        "girl_name": girl.name,
        "user_name": user.name,
        "overall_score": result.overall_score,
        "dimensions": result.dimensions,
        "summary": result.summary,
        "suggestion": result.suggestion,
        "search_results": result.search_results or [],
        "share_id": share_id or "",
        "beauty_sid": beauty_sid if (girl_photo or user_photo) else "",
        "beauty_pending": bool(girl_photo or user_photo),
    })


@app.get("/api/beauty-status/{share_id}")
async def beauty_status(share_id: str):
    """轮询颜值分析结果。"""
    import json as _json
    result = _beauty_cache.get(share_id)
    if result is None:
        return HTMLResponse(content='{"status":"pending"}', media_type="application/json")
    if isinstance(result, dict) and result.get("error"):
        return HTMLResponse(content='{"status":"error"}', media_type="application/json")
    return HTMLResponse(content=_json.dumps({"status":"done","data":result}, ensure_ascii=False), media_type="application/json")


@app.post("/api/share")
async def create_share(request: Request):
    """接收 JSON 分析结果，保存并返回短 ID。"""
    import json as _json
    body = await request.body()
    data = _json.loads(body)
    share_id = save_share(data)
    return {"id": share_id}


@app.get("/s/{share_id}", response_class=HTMLResponse)
async def view_share(request: Request, share_id: str):
    """查看分享页。"""
    data = get_share(share_id)
    if data is None:
        return HTMLResponse(
            content='<html><body style="background:#1a0a14;color:#e8d5d0;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif"><div><h1>404</h1><p>该分享不存在或已过期</p><a href="/" style="color:#d4847a;">返回首页</a></div></body></html>',
            status_code=404
        )
    return templates.TemplateResponse("share.html", {
        "request": request,
        **data,
    })


# ── 启动入口 ──────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    # 检查 API Key
    if not DEEPSEEK_API_KEY:
        print("=" * 55)
        print("[WARN] 未设置 DeepSeek API Key!")
        print("")
        print("请通过以下方式之一提供密钥:")
        print("  1) 命令行:  python main.py --api-key sk-xxx")
        print("  2) 环境变量: set DEEPSEEK_API_KEY=sk-xxx")
        print("  3) .env 文件: 在项目根目录创建 .env 并写入")
        print("               DEEPSEEK_API_KEY=sk-xxx")
        print("")
        print("获取免费 API Key: https://platform.deepseek.com")
        print("=" * 55)
        print("")

    from config import QWEN_API_KEY
    if not QWEN_API_KEY:
        print("[INFO] 未设置 Qwen API Key（截图OCR/颜值评分不可用）")
        print("      命令行: python main.py --qwen-api-key sk-xxx")
        print("      获取免费 Key: https://dashscope.aliyun.com/")
        print("")

    print(f"Server starting at http://{HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
