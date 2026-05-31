# 灵魂契合度分析 — 使用指南

## 目录

- [快速开始](#快速开始)
- [前置条件](#前置条件)
- [获取 DeepSeek API Key](#获取-deepseek-api-key)
- [配置说明](#配置说明)
- [启动服务](#启动服务)
- [使用流程](#使用流程)
- [分析维度说明](#分析维度说明)
- [分数等级](#分数等级)
- [网络搜索功能](#网络搜索功能)
- [发布到互联网](#发布到互联网)
- [常见问题](#常见问题)

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务（命令行传入两个 Key，不落盘）
python main.py --api-key sk-你的DeepSeek密钥 --qwen-api-key sk-你的Qwen密钥

# Qwen Key 可选（不传则截图OCR和颜值评分不可用）
python main.py --api-key sk-你的密钥

# 3. 浏览器打开
# http://localhost:8000
```

---

## 前置条件

| 项目 | 要求 |
|------|------|
| Python | ≥ 3.11 |
| pip | 最新版本 |
| 网络 | 能访问 `api.deepseek.com` 和 DuckDuckGo |

---

## 获取 DeepSeek API Key

1. 打开 [platform.deepseek.com](https://platform.deepseek.com)
2. 注册账号并登录
3. 进入控制台 → **API Keys** → 点击 **创建 API Key**
4. 复制生成的 Key（格式为 `sk-xxxxxxxx`）
5. 启动时通过命令行传入：

```bash
python main.py --api-key sk-你的密钥
```

> 💰 DeepSeek API 按 token 计费，价格极低。每次分析约消耗 2000-3000 token，成本不到 ¥0.01。

### 三种传入 API Key 的方式

| 方式 | 命令 | 适用场景 |
|------|------|----------|
| **命令行参数** | `python main.py --api-key sk-xxx` | 推荐，密钥不落盘 |
| **环境变量** | `set DEEPSEEK_API_KEY=sk-xxx` 后启动 | 使用 uvicorn 直接启动时 |
| **.env 文件** | `cp .env.example .env` 编辑后启动 | 开发环境，不想每次输入 |

> ⚠️ `.env` 文件已在 `.gitignore` 中，但如果你在意安全，优先使用命令行参数方式。

---

## 配置说明

### 命令行参数（推荐）

| 参数 | 说明 | 示例 |
|------|------|------|
| `--api-key` | DeepSeek API 密钥（必填） | `--api-key sk-xxx` |
| `--qwen-api-key` | Qwen 视觉 API 密钥（可选，截图OCR/颜值需要） | `--qwen-api-key sk-xxx` |
| `--host` | 服务监听地址 | `--host 127.0.0.1` |
| `--port` | 服务端口 | `--port 3000` |

```bash
python main.py --api-key sk-xxx --qwen-api-key sk-xxx
```

### .env 文件（可选）

`.env.example` 中可配置以下项目：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | API 密钥 | 无 |
| `DEEPSEEK_BASE_URL` | API 地址（也可用于代理） | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 使用的模型 | `deepseek-chat` |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |

> 命令行参数优先级高于 `.env` 文件。

**使用代理的示例**（在 `.env` 中）：
```
DEEPSEEK_BASE_URL=https://your-proxy.com/v1
```

`config.py` 中的搜索常量（一般不需要修改）：

| 常量 | 说明 | 默认值 |
|------|------|--------|
| `SEARCH_MAX_RESULTS` | 每次搜索返回条数 | 5 |
| `SEARCH_REQUEST_DELAY` | 搜索间隔（秒） | 1.0 |

---

## 启动服务

### 命令行启动（推荐，密钥不落盘）

```bash
# 基础启动
python main.py --api-key sk-你的密钥

# 指定端口
python main.py --api-key sk-你的密钥 --port 3000
```

### 环境变量 + uvicorn

```bash
# Windows
set DEEPSEEK_API_KEY=sk-你的密钥
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### .env + uvicorn

```bash
cp .env.example .env
# 编辑 .env 填入密钥后
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
python main.py --api-key sk-xxx
uvicorn main:app --host 0.0.0.0 --port 8000  # 不加 --reload
```

启动后在浏览器打开 `http://localhost:8000` 即可看到表单页面。

---

## 使用流程

### 第一步：选择示例或填写信息

打开首页后，你可以：

- **一键填充示例**：点击标签栏中的示例（如"🎨 文艺×理工"），预览后确认填充，表单自动填好。系统内置 4 组示例
- **📷 截图导入**：点击卡片右上角按钮，上传社交主页/交友资料截图，AI 自动提取信息填入表单。也支持在页面任意位置 Ctrl+V 粘贴截图
- 也可以手动填写：
  - **姓名/昵称**（必填）— 用于网络搜索和报告展示
  - **学历**：下拉选择学位等级（本科/硕士/博士等），输入学校名自动补全并显示 985/211/双一流标签
  - **照片**：点击上传区添加照片（选填），用于颜值评分
  - 年龄、家乡、职业、外貌特征（选填）
  - 性格描述、兴趣爱好、价值观（选填，但越详细分析越准）

### 第二步：填写你的信息

同样的表单结构，填写你自己的信息。

### 颜值 PK（独立功能）

访问 `/beauty` 页面，上传双方照片即可获取 AI 颜值评分、肤质脸型分析、颜值匹配度。无需填写文字信息。

### 第三步：选择是否启用网络搜索

默认勾选「启用网络搜索」，系统会用女方的姓名 + 职业/家乡/学历组合关键词在 DuckDuckGo 搜索公开信息，作为 LLM 分析的补充参考。

> ⚠️ 如果女方姓名是昵称或不方便搜索，建议取消勾选。

### 第四步：提交并等待

点击「开始匹配分析」，系统依次执行：

1. 全屏搜索动画 → 搜索她的公开信息，显示进度条
2. 搜索结果卡片 → 展示找到的信息，可勾选/取消，也可跳过
3. 确认后调用 DeepSeek API 分析 → 约 3-10 秒
4. 返回分析报告页面

### 第五步：查看报告

报告页面展示：

- 📊 **环形图** — 综合匹配度分数（0-100）
- 🏷️ **等级标签** — 高度契合 / 比较匹配 / 有一定基础 / 差异较大
- 📈 **维度条** — 5 个维度的得分柱状图 + 文字说明
- 📝 **综合评语** — AI 生成的总体分析
- 💡 **发展建议** — AI 给出的关系建议
- 🌐 **网络参考信息** — 搜索到的公开资料（如有）
- 📋 **分享栏** — 复制链接发给朋友看（底部）

### 明暗主题切换

页面右上角有一个圆形按钮，点击可在两种主题间切换：

| 图标 | 主题 | 风格 |
|------|------|------|
| ☀️ | 暗夜浪漫 | 深酒红底 + 玫瑰金文字，毛玻璃卡片 |
| 🌙 | 日暖浪漫 | 奶油白底 + 暖棕玫瑰，柔和明亮 |

选择会被浏览器自动记住，下次打开无需重新设置。

---

## 分析维度说明

| 维度 | 分析内容 |
|------|----------|
| 性格契合度 | 双方性格是否互补或相似，沟通方式是否匹配 |
| 价值观契合度 | 人生目标、金钱观、家庭观是否一致 |
| 兴趣爱好契合度 | 共同兴趣点，空闲时间的活动偏好 |
| 生活方式契合度 | 作息习惯、社交频率、消费观念 |
| 成长背景契合度 | 家乡、学历、家庭背景的相似程度 |

---

## 分数等级

| 分数 | 等级 | 含义 |
|------|------|------|
| 85-100 | 💚 高度契合 | 两人各方面匹配度很高，发展潜力大 |
| 75-84 | 💛 比较匹配 | 有良好基础，少量差异可磨合 |
| 60-74 | 🧡 有一定基础 | 部分匹配，需进一步了解 |
| 0-59 | ❤️ 差异较大 | 关键维度差异明显，需要更多沟通 |

---

## 网络搜索功能

### 工作原理

- 使用 DuckDuckGo 搜索引擎（免费，无需 API Key）
- 搜索关键词：`女方姓名 + 职业 + 学历 + 家乡`
- 最多返回 5 条结果
- 搜索到的片段会附加到 LLM prompt 中，作为公开背景信息

### 适用场景

| 场景 | 建议 |
|------|------|
| 女方为公众人物或网上有公开资料 | ✅ 开启 |
| 女方为普通用户，使用真实姓名 | ✅ 开启 |
| 使用昵称/网名 | ❌ 关闭（搜不到有效信息） |
| 注重隐私 | ❌ 关闭 |

### 注意事项

- DuckDuckGo 有频率限制，短时间内多次搜索可能被短暂限制
- 搜索结果仅供参考，LLM 不会将其作为主要判断依据
- Python 库 `ddgs` 是同步的，代码通过 `asyncio.to_thread` 在线程池中执行，不会阻塞主事件循环

---

## 发布到互联网

本地启动的服务只有你自己能访问（`localhost:8000`）。要让朋友也能打开，需要一个**公网地址**。以下是本项目实际使用的方案：

### 实战：Cloudflare Tunnel（推荐）

这是本项目实际采用的方式。原理：Cloudflare 在你的电脑和它的全球边缘节点之间建立一条加密隧道，外部请求通过隧道转发到你的本地服务，全程 HTTPS 自动加密。

**第一步：启动 soul_match**

```bash
# 终端 1：正常启动服务
python main.py --api-key sk-xxx
# 输出：Uvicorn running on http://0.0.0.0:8000
```

**第二步：安装 Cloudflare 隧道客户端**

```bash
winget install cloudflare.cloudflared
```

安装完成后**重启终端**使命令生效。

**第三步：启动隧道**

```bash
# 终端 2：启动隧道
cloudflared tunnel --url localhost:8000
```

输出：

```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at:                                          |
|  https://bold-roller-voted-foundations.trycloudflare.com                                   |
+--------------------------------------------------------------------------------------------+
```

**第四步：分享**

把 `https://bold-roller-voted-foundations.trycloudflare.com` 发给任何人，他们就能打开你的 soul_match 网页。

> ⚠️ 免费版每次重启隧道 URL 会变。如需固定域名，注册 Cloudflare 账号创建命名隧道即可（详见 `docs/PORT-FORWARDING.md`）。

**本地 vs 公网访问对比：**

```
你电脑上的浏览器 → http://localhost:8000         ✅ 只有你能访问
朋友手机/电脑    → https://xxx.trycloudflare.com  ✅ 全球都能访问
```

### 其他方案

| 方案 | 命令 | 费用 | 特点 |
|------|------|------|------|
| **Cloudflare Tunnel** | `cloudflared tunnel --url localhost:8000` | 免费 | ✅ 本项目推荐 |
| **Localtunnel** | `npx localtunnel --port 8000` | 免费 | 零安装，临时用 |
| **ngrok** | `ngrok http 8000` | 免费有限制 | 有 Web 调试面板 |

更详细的对比和配置见 **[docs/PORT-FORWARDING.md](PORT-FORWARDING.md)**。

### 部署到云服务器

```bash
git clone <your-repo-url>
cd soul_match
pip install -r requirements.txt
```

`/etc/systemd/system/soulmatch.service`:
```ini
[Unit]
Description=灵魂契合度分析服务
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/soul_match
Environment="DEEPSEEK_API_KEY=sk-你的密钥"
ExecStart=/usr/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable soulmatch && sudo systemctl start soulmatch
```

然后配置 Nginx 反向代理 + Let's Encrypt HTTPS 证书。

---

## 常见问题

### Q: 启动时报 `ImportError: No module named 'ddgs'`

```bash
pip install -r requirements.txt
```

如果 `ddgs` 安装失败，可以尝试：

```bash
pip install ddgs --upgrade
```

### Q: 提交后显示「未配置 DeepSeek API Key」

- 如果用 `python main.py` 启动，检查是否传了 `--api-key` 参数
- 如果用 `uvicorn` 启动，检查是否设置了环境变量或 `.env` 文件
- 如果 `.env` 已配置但未生效，确认 `.env` 文件在项目根目录

### Q: 提交后显示「分析服务暂时不可用」

可能原因：
1. API Key 无效或余额不足
2. 网络无法访问 `api.deepseek.com`

检查方法：
```bash
python -c "from config import DEEPSEEK_API_KEY; print('OK' if DEEPSEEK_API_KEY else 'MISSING')"
```

### Q: 网络搜索没有返回结果

- DuckDuckGo 在中国大陆可能需要代理
- 搜索词可能太模糊，尝试更具体的姓名
- 临时被限流，稍等片刻再试

### Q: 分析结果不准确

- 尽量详细填写双方的性格、兴趣、价值观描述
- LLM 基于你提供的信息分析，信息越丰富越准确
- 结果仅供娱乐参考，不代表真实情况

### Q: 如何更换 LLM 模型？

编辑 `.env` 中的 `DEEPSEEK_MODEL`：
```
# 使用深思考模式（更深入但更慢）
DEEPSEEK_MODEL=deepseek-reasoner
```

也可以换成其他兼容 OpenAI 接口的 API：
```
DEEPSEEK_BASE_URL=https://api.openai.com/v1
DEEPSEEK_MODEL=gpt-4o
DEEPSEEK_API_KEY=sk-your-openai-key
```

### Q: 如何修改分析维度？

编辑 `services/llm_service.py` 中的 `SYSTEM_PROMPT`，修改 `dimensions` 部分即可自定义分析维度。
