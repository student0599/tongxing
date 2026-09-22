# 瞳行 —— 容器化部署镜像
# 适用于 Hugging Face Spaces / Render / Railway / 任意云主机 等平台
FROM python:3.11-slim

WORKDIR /app

# 先装依赖，利用 Docker 层缓存加速构建
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码（.env 已被 .dockerignore 排除，密钥请通过平台 Secrets 注入）
COPY . .

EXPOSE 8501

# 健康检查：探测 Streamlit 内置健康端点
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3).status==200 else 1)"

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
