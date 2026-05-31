#!/bin/bash
# soul_match 公网隧道启动脚本（自动切换）
# 用法: bash tunnel.sh
# 依赖: cloudflared 或 npx（二选一可用即可）

PORT=${PORT:-8000}

echo "🔗 启动公网隧道（端口: $PORT）..."
echo ""

# 优先 Cloudflare Tunnel
if command -v cloudflared &> /dev/null; then
    echo "→ 尝试 Cloudflare Tunnel（免费，HTTPS）..."
    cloudflared tunnel --url localhost:$PORT 2>&1
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        exit 0
    fi
    echo "⚠️  Cloudflare Tunnel 退出（exit code: $EXIT_CODE）"
fi

# 备选 Localtunnel
echo "→ 切换到 Localtunnel（免费，HTTPS）..."
npx localtunnel --port $PORT
