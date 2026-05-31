#!/bin/bash
# soul_match 公网隧道启动脚本
# 用法: bash tunnel.sh
# 固定域名: https://soulmatch.20260816.xyz

PORT=${PORT:-8000}

echo "🔗 启动公网隧道（端口: $PORT）..."
echo ""

# 方案1：Cloudflare 命名隧道（固定域名，大文件支持）
if command -v cloudflared &> /dev/null && [ -f ~/.cloudflared/cert.pem ]; then
    echo "→ Cloudflare 命名隧道 → https://soulmatch.20260816.xyz"
    cloudflared tunnel run --url localhost:$PORT --protocol http2 soulmatch
    exit $?
fi

# 方案2：Localtunnel（备用，随机域名）
if command -v npx &> /dev/null; then
    echo "→ Localtunnel（备用，随机域名）..."
    npx localtunnel --port $PORT
    exit $?
fi

echo "❌ 未找到 cloudflared 或 npx"
exit 1
