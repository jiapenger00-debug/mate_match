# Windows 下 Cloudflare Tunnel 安装与配置实录

> 记录在 Windows 11 上安装 cloudflared 并实现 soul_match 公网访问的完整过程

## 环境

- OS: Windows 11 家庭中文版 10.0.26200
- Shell: Git Bash（通过 VS Code 终端）
- 项目: soul_match（FastAPI，端口 8000）

## 步骤 1：安装 cloudflared

使用 Windows 包管理器 winget 安装：

```bash
winget install cloudflare.cloudflared --accept-source-agreements
```

输出：

```
已找到 cloudflared [Cloudflare.cloudflared] 版本 2026.5.2
正在下载 https://github.com/cloudflare/...cloudflared-windows-amd64.exe
已成功验证安装程序哈希
已成功安装
```

安装完成后 winget 提示：

```
已修改路径环境变量；重启 shell 以使用新值。
添加了命令行别名："cloudflared"
```

## 步骤 2：验证安装（遇到问题）

重启终端后运行：

```bash
$ cloudflared --version
bash: cloudflared: command not found
```

**问题：** winget 虽然提示"已修改路径环境变量"，但实际 PATH 未生效。

**排查：** 查找 cloudflared 实际安装位置：

```bash
$ find /c/Users/13555/AppData -name "cloudflared.exe" -type f
/c/Users/13555/AppData/Local/Microsoft/WinGet/Packages/
  Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe/cloudflared.exe
```

文件存在于 WinGet 的包管理目录，但该目录不在 PATH 中。

## 步骤 3：修复 PATH

尝试了三种方案：

| 方案 | 命令 | 结果 |
|------|------|------|
| `setx` CMD | `cmd //c "setx PATH \"...\""` | 失败，编码语法错误 |
| 复制到 System32 | `cp cloudflared.exe /c/Windows/System32/` | 失败，需要管理员权限 |
| **PowerShell 写用户 PATH** | `[Environment]::SetEnvironmentVariable(...)` | ✅ 成功 |

最终使用 PowerShell 写入用户环境变量：

```powershell
[Environment]::SetEnvironmentVariable(
    'Path',
    [Environment]::GetEnvironmentVariable('Path', 'User') +
    ';' + $env:LOCALAPPDATA + '\Microsoft\WinGet\Links',
    'User'
)
```

这会将 `%LOCALAPPDATA%\Microsoft\WinGet\Links` 追加到当前用户的 PATH 环境变量中，而 WinGet 安装时已经在该目录下创建了 `cloudflared.exe` 的快捷方式。

重启终端后 `cloudflared --version` 正常工作。

## 步骤 4：启动隧道

确保 soul_match 服务已启动（`python main.py --api-key sk-xxx`），然后：

```bash
cloudflared tunnel --url localhost:8000
```

输出：

```
2026-05-31T05:17:17Z INF Requesting new quick Tunnel on trycloudflare.com...
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at:                                          |
|  https://bold-roller-voted-foundations.trycloudflare.com                                   |
+--------------------------------------------------------------------------------------------+
```

## 步骤 5：验证公网可访问

```bash
curl -s -o /dev/null -w "%{http_code}" https://bold-roller-voted-foundations.trycloudflare.com/
# 输出：200（首次可能返回 502/530，稍等几秒重试即可）
```

**踩坑记录：** 刚创建隧道时连续遇到 530（origin unreachable）和 502 错误，原因是：

1. 隧道建立后需要几秒时间在全球 CDN 节点间同步
2. 若启动时用了 `--no-tls-verify` 标志反而会导致握手失败
3. 正确做法：直接 `cloudflared tunnel --url localhost:8000`，不加任何额外参数，等待 5-10 秒后访问

## 架构原理

```
用户手机/电脑                    Cloudflare 全球 CDN               你的 Windows 电脑
┌──────────┐                    ┌──────────────────┐              ┌──────────────┐
│ 浏览器    │ ──HTTPS──→        │ trycloudflare.com │ ──QUIC──→   │ cloudflared  │
│          │ ←──HTTPS──        │  (边缘节点)        │ ←──QUIC──   │ (本地客户端)  │
└──────────┘                    └──────────────────┘              └──────┬───────┘
                                                                       │ HTTP
                                                                       ▼
                                                              ┌──────────────┐
                                                              │ localhost:8000│
                                                              │ (soul_match)  │
                                                              └──────────────┘
```

1. `cloudflared` 在本地启动后，主动向 Cloudflare 全球网络发起 QUIC 连接
2. Cloudflare 分配一个临时域名（`xxx.trycloudflare.com`）
3. 外部请求到达 Cloudflare 边缘节点 → 通过 QUIC 隧道转发到你的电脑 → 交给 `localhost:8000`
4. 全程 HTTPS 加密，无需配置证书，无需路由器端口映射

## 常用操作

```bash
# 启动隧道（每次重启 URL 会变）
cloudflared tunnel --url localhost:8000

# 查看版本
cloudflared --version

# 更新
winget upgrade cloudflare.cloudflared
```
