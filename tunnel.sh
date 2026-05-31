#!/bin/bash
# soul_match 隧道启动脚本
# 依赖：cloudflared 已安装并配置到 PATH

echo "🚀 启动 Cloudflare Tunnel..."
echo "确保 Python 服务已在另一个终端运行：python main.py --api-key sk-xxx"
echo ""
cloudflared tunnel --url localhost:8000
