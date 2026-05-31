# soul_match v1.3 — 补充分析功能 · 设计文档

> 日期：2026-05-31  
> 分支：`feat/supplement-analysis`

---

## 概述

匹配分析完成后，在结果页底部提供「补充信息，进一步分析」按钮。点击弹出模态框，用户可选择补充对象（她/他）、输入自由文本、上传照片或截图 OCR 识别，提交后 LLM 结合原始报告和补充信息重新分析，结果在原页面上更新。

## 交互流程

```
结果页底部分享栏下方
  │
  └─ [📝 补充信息，进一步分析]
        │
        ▼
    ┌─ 模态弹窗 ────────────────────┐
    │ ✕ 关闭                        │
    │ 补充对象:  [👩 她] [🧑 他]    │
    │                                │
    │ 文字补充:                      │
    │ ┌────────────────────────┐    │
    │ │ 自由输入任何补充信息…    │    │
    │ └────────────────────────┘    │
    │                                │
    │ [📷 上传照片] [📋 截图OCR]    │
    │ 上传后显示文件名               │
    │                                │
    │ [🔍 进一步分析]               │
    └────────────────────────────────┘
        │ POST /api/supplement
        ▼
  LLM 重新分析 → 结果页局部更新
```

## 后端

### 新增路由

`POST /api/supplement` — 接收补充数据 + share_id，返回新分析结果

| 参数 | 类型 | 说明 |
|------|------|------|
| `share_id` | str | 原始报告的短 ID |
| `target` | str | `girl` 或 `user` |
| `text` | str | 补充文本（选填） |
| `photo` | file | 补充照片（选填） |

后端逻辑：
1. 根据 `share_id` 从 SQLite 读取原始分析数据
2. 若有照片 → 压缩后调用 Qwen OCR 提取描述（如有）
3. 组装完整上下文：原始信息 + 原报告摘要 + 补充文本 + 照片描述
4. 调用 DeepSeek LLM 生成新的分析报告
5. 返回完整的新 `AnalyzeResponse` JSON

### vision_service 新增

`analyze_supplement_photo(image_bytes)` — 对补充照片生成描述文本（非颜值评分，而是"What can you tell about this person from this photo"类型的客观描述），嵌入到补充上下文中。

### 不变

- 原始 share 数据不修改
- 返回的新分析结果不覆盖旧分享（可以在结果页展示新结果，但分享链接仍指向原报告）

## 前端

### result.html 改动

在分享栏下方、返回按钮上方新增：

```html
<button class="btn supplement-btn" onclick="openSupplement()">
    📝 补充信息，进一步分析
</button>
```

### 模态弹窗

纯 CSS + JS，内嵌在 result.html 中（无需新模板文件）。结构：
- `.supplement-overlay` — 全屏半透明遮罩
- `.supplement-modal` — 居中弹窗卡片
- 对象选择标签（她/他）
- 文本域
- 上传按钮 + OCR 按钮
- 提交按钮

JS 逻辑：
- `openSupplement()` → 显示弹窗
- OCR/照片上传复用已有 `compressImage` + `/api/ocr`
- 提交 → fetch POST `/api/supplement` → 拿到新分析结果 → 更新页面 DOM

### 结果页更新

新分析结果返回后，不刷新整页，而是用 JS 替换：
- 综合匹配度数字
- 维度条
- 综合评语 + 发展建议
- 新增一行提示「基于补充信息重新分析」

### 文件变化

| 文件 | 操作 |
|------|------|
| `main.py` | 新增 `POST /api/supplement` |
| `services/vision_service.py` | 新增 `analyze_supplement_photo()` |
| `templates/result.html` | 新增按钮 + 弹窗 HTML + JS |
| `static/style.css` | 新增弹窗 + 补充按钮样式 |
