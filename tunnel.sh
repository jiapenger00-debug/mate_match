#!/bin/bash
# soul_match 公网隧道启动脚本
# 用法: bash tunnel.sh
# 如果用到固定域名的话，需要将固定域名放到环境变量中，示例：
# export SOULMATCH_DOMAIN=soulmatch.20260816.xyz  # ← 取消注释使用固定域名

PORT=${PORT:-8000}

echo "🔗 启动公网隧道（端口: $PORT）..."
echo ""

# 方案1：Cloudflare 命名隧道（固定域名，需提前配置证书+DNS）
if command -v cloudflared &> /dev/null && [ -f ~/.cloudflared/cert.pem ]; then
    if [ -n "$SOULMATCH_DOMAIN" ]; then
        echo "→ Cloudflare 命名隧道 → https://$SOULMATCH_DOMAIN"
    else
        echo "→ Cloudflare 命名隧道（随机域名）"
    fi
    cloudflared tunnel run --url localhost:$PORT --protocol http2 soulmatch
    exit $?
fi

# 方案2：Localtunnel（备用，零门槛，随机域名）
if command -v npx &> /dev/null; then
    echo "→ Localtunnel（备用，随机域名）..."
    npx localtunnel --port $PORT
    exit $?
fi

echo "❌ 未找到 cloudflared 或 npx"
exit 1
