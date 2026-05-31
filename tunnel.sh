#!/bin/bash
# soul_match 公网隧道启动脚本（多方案自动切换）
# 用法: bash tunnel.sh
# 依赖: ssh / cloudflared / npx（有一个即可）

PORT=${PORT:-8000}

echo "🔗 启动公网隧道（端口: $PORT）..."
echo ""

# 方案1：Serveo（零安装，可固定域名）
if command -v ssh &> /dev/null; then
    echo "→ 尝试 Serveo（SSH 隧道，可固定子域名）..."
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -R soulmatch:80:localhost:$PORT serveo.net 2>&1
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 130 ]; then
        exit 0
    fi
    echo "⚠️  Serveo 退出（exit code: $EXIT_CODE）"
fi

# 方案2：Cloudflare Tunnel
if command -v cloudflared &> /dev/null; then
    echo "→ 尝试 Cloudflare Tunnel（免费，HTTPS）..."
    cloudflared tunnel --url localhost:$PORT 2>&1
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        exit 0
    fi
    echo "⚠️  Cloudflare Tunnel 退出（exit code: $EXIT_CODE）"
fi

# 方案3：Localtunnel
echo "→ 切换到 Localtunnel（免费，HTTPS）..."
npx localtunnel --port $PORT
