# Self-Healing System API Dockerfile
# 多阶段构建，优化镜像大小和安全性

# 构建阶段
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.11-slim as runtime

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安装运行时依赖（最小化安装）
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建必要的目录并设置Python路径
RUN mkdir -p /var/log/self-healing /var/lib/self-healing /tmp/playbook_executions && \
    chown -R appuser:appuser /app /var/log/self-healing /var/lib/self-healing /tmp/playbook_executions

# 设置Python路径环境变量
ENV PYTHONPATH=/app:/app/api

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]