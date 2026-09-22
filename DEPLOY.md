# 瞳行 · 公网部署指南

> 比赛要求：作品须具备公网连通性，仅限局域网/校园网访问的作品视为无效。
> 本指南提供三种把「瞳行」部署到公网的方案，按推荐度排序。

---

## 方案选择速查

| 方案 | 成本 | 国内访问速度 | 手机拍照(HTTPS) | 结论 |
|---|---|---|---|---|
| **A. Streamlit Community Cloud** | 免费 | 一般 | ✅ | **首选**，零运维 |
| **B. 国内云服务器** | 少量费用 | 快 | 需域名+备案 | 追求稳定流畅 |
| **C. Cloudflare Tunnel** | 免费 | 视线路 | ✅ | 答辩现场临时演示 |

> ⚠️ 关键：手机端 `st.camera_input` 拍照**必须 HTTPS**。A/C 方案自动提供 HTTPS；B 方案用纯 IP 无 HTTPS，需域名 + 备案 + 证书。

---

## 方案 A：Streamlit Community Cloud（免费，首选）

### A1. 把代码推送到 GitHub

```bash
cd /d/competition
git init
git add .
git commit -m "feat: 瞳行 视障出行AI辅助智能体"
git branch -M main
git remote add origin https://github.com/<你的用户名>/tongxing.git
git push -u origin main
```

> `.env`、`.streamlit/secrets.toml` 已在 `.gitignore` 中排除，密钥不会上传。

### A2. 在 Streamlit Cloud 部署

1. 打开 <https://share.streamlit.io>，用 GitHub 账号登录。
2. 点击 **New app** → 选择刚推送的仓库。
3. **Main file path** 填：`app.py`。
4. 展开 **Advanced settings**，在 **Secrets** 中填入：

```toml
ZHIPU_API_KEY = "你的智谱API Key"
EMERGENCY_CONTACT_NAME = "家人"
EMERGENCY_CONTACT_PHONE = "13800000000"
```

5. 点击 **Deploy**，约 1~2 分钟后获得公网地址：`https://<应用名>.streamlit.app`。

### A3. 验收

- ✅ 公网 URL 可打开（用手机流量关闭 WiFi 测试，确保非局域网）
- ✅ 手机拍照可用（HTTPS 已就绪）
- ✅ 联网功能：环境识别 / 文字朗读 / 紧急求助均调用云端 API

> 注意：免费版应用长时间无人访问会「休眠」，首次打开需数秒唤醒，属正常现象。评审前先访问一次「预热」即可。

---

## 方案 B：国内云服务器（最流畅，需少量费用）

适合对「流畅运行」要求极高的情况。推荐阿里云/腾讯云**轻量应用服务器**（有学生优惠）。

### B1. 服务器环境

```bash
# Ubuntu 22.04 上安装 Python 3.11 与 pip
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx
```

### B2. 部署应用

```bash
sudo mkdir -p /opt/tongxing && cd /opt/tongxing
# 上传代码后
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

创建 `/etc/systemd/system/tongxing.service`：

```ini
[Unit]
Description=TongXing Streamlit App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/tongxing
Environment="ZHIPU_API_KEY=你的Key"
ExecStart=/opt/tongxing/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tongxing
```

### B3. Nginx 反向代理 + HTTPS

```nginx
server {
    listen 443 ssl;
    server_name tongxing.example.com;   # 需已备案域名

    ssl_certificate     /etc/ssl/tongxing.pem;
    ssl_certificate_key /etc/ssl/tongxing.key;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 300;
    }
}
```

> HTTPS 证书可用 Let's Encrypt（`certbot`）免费申请，但**域名需已完成 ICP 备案**才能在国内服务器稳定提供服务。

### 也可用 Docker 一键部署

```bash
docker build -t tongxing .
docker run -d -p 8501:8501 -e ZHIPU_API_KEY=你的Key tongxing
```

---

## 方案 C：Cloudflare Tunnel（免费，临时演示）

适合答辩当天把本地机器临时暴露到公网，无需服务器、无需备案。

```bash
# 1. 安装 cloudflared（https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/）
# 2. 本地启动应用
streamlit run app.py

# 3. 快速隧道（临时随机域名，HTTPS 自动）
cloudflared tunnel --url http://localhost:8501
```

运行后终端会输出一个 `https://xxxxx.trycloudflare.com` 公网地址，可直接发给评审。

> 缺点：地址每次重启会变，适合临时演示而非长期评审。如需固定域名，可绑定自有域名（免备案，走 Cloudflare 加速）。

---

## 部署后自检清单

- [ ] 用**手机流量**（关闭 WiFi）打开公网 URL，确认非局域网也能访问
- [ ] 手机拍照功能可用（地址栏是 `https://`）
- [ ] 环境识别 / 文字朗读 / 紧急求助任一功能跑通一次（验证云端 API 连通）
- [ ] 密钥通过平台 Secrets / 环境变量注入，**未硬编码进代码、未提交进仓库**
