# 端口转发与公网访问指南

> 如何让本地运行的 soul_match 服务暴露到公网，方便朋友远程访问

---

## 方式一：Localtunnel（推荐，稳定免费）

零安装，一条命令，支持大文件上传（截图 OCR、颜值分析）。

```bash
npx localtunnel --port 8000
```

首次访问会有一个提示页，点击「Click to Continue」即可。实测最稳定。

---

## 方式二：Cloudflare Tunnel（免费，偶尔不稳）

### 安装

```bash
winget install cloudflare.cloudflared
```

安装后需**重启终端**使 `cloudflared` 命令生效。

### 使用

确保 soul_match 服务正在运行（`http://localhost:8000`），然后：

```bash
cloudflared tunnel --url localhost:8000
```

输出示例：

```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at:                                          |
|  https://bold-roller-voted-foundations.trycloudflare.com                                   |
+--------------------------------------------------------------------------------------------+
```

把这个 `https://xxx.trycloudflare.com` 链接发给任何人就能访问你的服务。

### 特点

| 优势 | 劣势 |
|------|------|
| 完全免费，不限流量 | 免费版无 SLA，偶尔 502 |
| HTTPS 自动加密 | 每次重启 URL 会变（隧道不关则不变） |
| 无需注册账号 | 固定域名需绑定信用卡（见下方说明） |

### 关于固定域名

免费临时隧道已满足日常分享。如需固定域名，必须注册 Cloudflare 账号并绑定境外信用卡（实测需 VISA/MasterCard 验证），然后创建命名隧道。**不推荐，性价比不高。**

如果需要固定域名，注册免费 Cloudflare 账号后创建命名隧道：

```bash
# 登录
cloudflared login

# 创建隧道
cloudflared tunnel create soulmatch

# 配置 DNS 指向隧道
cloudflared tunnel route dns soulmatch soulmatch.yourdomain.com

# 运行
cloudflared tunnel run soulmatch --url localhost:8000
```

---

## 方式二：Localtunnel（最简单，一行命令）

无需安装任何东西，直接通过 npx 运行：

```bash
npx localtunnel --port 8000
```

输出：

```
your url is: https://xxxx.loca.lt
```

### 特点

| 优势 | 劣势 |
|------|------|
| 零安装，一条命令 | 每次 URL 会变 |
| 免费 | 偶尔不稳定 |
| 有访问密码页面 | 中国大陆可能被墙 |

---

## 方式三：ngrok

### 安装

```bash
winget install ngrok.ngrok
```

### 使用

```bash
ngrok http 8000
```

### 特点

| 优势 | 劣势 |
|------|------|
| 功能丰富，支持 Web 界面 | 免费版有流量限制（约 1GB/月） |
| 可固定域名（付费） | 需注册账号 |

---

## 方式四：frp（自建，最可控）

如果有自己的云服务器，用 frp 自建内网穿透。

### 服务端（云服务器）

```ini
# frps.toml
bindPort = 7000
vhostHTTPPort = 8080
```

### 客户端（本地）

```ini
# frpc.toml
serverAddr = "your-server-ip"
serverPort = 7000

[[proxies]]
name = "web"
type = "http"
localPort = 8000
customDomains = ["soulmatch.yourdomain.com"]
```

### 特点

| 优势 | 劣势 |
|------|------|
| 完全自控，稳定性最高 | 需要一台云服务器 |
| 可固定域名 + HTTPS | 配置较复杂 |

---

## 对比总结

| 方案 | 费用 | 稳定性 | 易用性 | 推荐场景 |
|------|------|--------|--------|----------|
| Cloudflare Tunnel | 免费 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 日常使用，推荐首选 |
| Localtunnel | 免费 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 快速临时分享 |
| ngrok | 免费有限制 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 需 Web 调试界面时 |
| frp | 需服务器 | ⭐⭐⭐⭐⭐ | ⭐⭐ | 生产环境长期部署 |

---

## 快速启动脚本

在项目根目录创建 `tunnel.sh`（Git Bash 使用）：

```bash
#!/bin/bash
echo "启动 soul_match 隧道..."
cloudflared tunnel --url localhost:8000
```

以后只需：

```bash
# 终端 1：启动服务
python main.py --api-key sk-xxx

# 终端 2：启动隧道
bash tunnel.sh
```
