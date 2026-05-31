# Cloudflare 命名隧道配置指南（固定域名）

> 从零开始，一步步配置永久公网地址。面向小白，保姆级教程。

## 你需要准备

| 项目 | 说明 |
|------|------|
| Cloudflare 账号 | 去 [cloudflare.com](https://cloudflare.com) 注册，需要绑定 VISA/MasterCard 验证身份（不扣费） |
| 一个域名 | 任意域名托管到 Cloudflare（购买或用已有的都行） |
| 本项目 | soul_match 已安装并能在 `http://localhost:8000` 运行 |

## 第一步：注册并绑定 Cloudflare

1. 打开 [cloudflare.com](https://cloudflare.com)，点击 **Sign Up**
2. 用邮箱注册，填写基本信息
3. 验证身份——需要绑定一张信用卡（VISA 或 MasterCard）。**不会扣费**，只是确认你是真人
4. 登录后，点击 **Add a Site**，输入你的域名（如 `20260816.xyz`）
5. 按引导把域名 DNS 托管到 Cloudflare（通常需要去你的域名注册商那里把 nameserver 改成 Cloudflare 提供的地址）

## 第二步：安装 cloudflared

```bash
winget install cloudflare.cloudflared
```

安装后重启终端生效。

## 第三步：获取证书

```bash
cloudflared tunnel login
```

浏览器会自动打开 Cloudflare 登录页。登录后证书会自动下载到 `C:\Users\你的用户名\.cloudflared\cert.pem`。

如果下载失败，手动去 Cloudflare 后台下载：

1. 打开 https://one.dash.cloudflare.com/
2. 左侧菜单 → **Access** → **Tunnels**
3. 页面右上角点击下载按钮 📥
4. 把下载的 `cert.pem` 放到 `C:\Users\你的用户名\.cloudflared\` 目录下

### 验证证书

```bash
ls -la ~/.cloudflared/cert.pem
```

应该显示一个几百字节的小文件，内容以 `-----BEGIN ARGO TUNNEL TOKEN-----` 开头。

## 第四步：创建命名隧道

```bash
cloudflared tunnel create soulmatch
```

成功后会输出类似：

```
Tunnel credentials written to C:\Users\xxx\.cloudflared\<tunnel-id>.json
Created tunnel soulmatch with id 82b4b62f-55bc-42e2-9401-a093e8ea4b26
```

记下这个 `<tunnel-id>`，下一步要用。

## 第五步：配置 DNS 记录

1. 打开 https://dash.cloudflare.com/
2. 选择你的域名
3. 左侧 **DNS** → **记录** → **添加记录**
4. 填写：

| 字段 | 值 |
|------|-----|
| 类型 | **CNAME** |
| 名称 | `soulmatch`（或你想要的子域名） |
| 目标 | `<tunnel-id>.cfargotunnel.com`（上一步得到的 ID） |
| 代理 | **开启**（橙色云朵） |

例如：名称 `soulmatch`，目标 `82b4b62f-55bc-42e2-9401-a093e8ea4b26.cfargotunnel.com`

保存后等几秒钟生效。

## 第六步：启动隧道

```bash
export SOULMATCH_DOMAIN=soulmatch.你的域名.xyz
cloudflared tunnel run --url localhost:8000 --protocol http2 soulmatch
```

或直接用项目脚本：

```bash
bash tunnel.sh
```

## 第七步：验证

浏览器打开 `https://soulmatch.你的域名.xyz`，看到 soul_match 首页就成功了。URL 永久不变，HTTPS 自动加密。

## 常见问题

### Q: 报错 "Authentication error" 怎么办？

证书 `cert.pem` 没放对位置或已过期。重新执行 `cloudflared tunnel login` 获取新证书。

### Q: 报错 502/530 怎么处理？

等几秒钟重试。刚配置完 DNS 需要一点时间全球生效。如果持续 502，可能是本地服务器没启动。

### Q: cloudflared 命令找不到？

```bash
winget install cloudflare.cloudflared
```

安装后**必须重启终端**。

### Q: 我没有域名怎么办？

用 Localtunnel（临时随机 URL）：`npx localtunnel --port 8000`
