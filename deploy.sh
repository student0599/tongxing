#!/bin/bash
# 瞳行 Streamlit 部署脚本（在 Ubuntu 云服务器上以 root 运行）
# 用法：把整个项目（含 .env）上传到服务器后，在项目根目录执行  bash deploy.sh
set -e

PORT=8501

echo "==> [1/5] 安装系统依赖"
apt-get update -y
apt-get install -y python3 python3-pip python3-venv

echo "==> [2/5] 创建虚拟环境并安装 Python 依赖"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

echo "==> [3/5] 生成 systemd 服务"
CURDIR=$(pwd)
cat > /etc/systemd/system/tongxing.service <<EOF
[Unit]
Description=TongXing Streamlit App
After=network.target

[Service]
WorkingDirectory=$CURDIR
ExecStart=$CURDIR/venv/bin/streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "==> [4/5] 启动并设置开机自启"
systemctl daemon-reload
systemctl enable tongxing
systemctl restart tongxing

echo "==> [5/5] 部署完成"
IP=$(curl -s --max-time 5 ifconfig.me || echo "你的服务器公网IP")
echo ""
echo "✅ 访问地址：http://$IP:$PORT"
echo "   查看日志：journalctl -u tongxing -f"
echo ""
echo "⚠️ 请确保云服务器「安全组/防火墙」已放行端口 $PORT"
