#!/bin/bash
# soul_match 隧道启动脚本
# 依赖：cloudflared 已安装并配置到 PATH
# 端口从 .env 读取，默认 8000

PORT=${PORT:-8000}

echo "🚀 启动 Cloudflare Tunnel (端口: $PORT)..."
echo "确保 Python 服务已在另一个终端运行"
echo ""
cloudflared tunnel --url localhost:$PORT
