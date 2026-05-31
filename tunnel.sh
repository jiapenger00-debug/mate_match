#!/bin/bash
# soul_match 公网隧道启动脚本
# 用法: bash tunnel.sh
# 依赖: npx（Node.js 自带）或 cloudflared

PORT=${PORT:-8000}

echo "🔗 启动公网隧道（端口: $PORT）..."
echo ""

# 方案1：Localtunnel（稳定，免费）
if command -v npx &> /dev/null; then
    echo "→ 使用 Localtunnel（免费 HTTPS，支持大文件上传）..."
    npx localtunnel --port $PORT
    exit $?
fi

# 方案2：Cloudflare Tunnel
if command -v cloudflared &> /dev/null; then
    echo "→ Cloudflare Tunnel（免费 HTTPS）..."
    cloudflared tunnel --url localhost:$PORT
    exit $?
fi

echo "❌ 未找到 npx 或 cloudflared，请安装 Node.js 或 cloudflared"
exit 1
