# 多阶段构建Dockerfile for 服务器热控制系统

# 构建阶段
FROM rust:1.75-slim as builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libsqlite3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制Cargo文件
COPY Cargo.toml Cargo.lock ./

# 创建虚拟源文件以缓存依赖
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# 复制源代码
COPY src ./src

# 构建应用程序
RUN cargo build --release

# 运行时阶段
FROM debian:bookworm-slim

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    libsqlite3-0 \
    ipmitool \
    lm-sensors \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN useradd -r -s /bin/false -m -d /app thermal

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/target/release/server_thermal_control /app/

# 创建必要的目录
RUN mkdir -p /app/config /app/data /app/logs && \
    chown -R thermal:thermal /app

# 复制配置文件
COPY config/app.toml /app/config/

# 设置权限
RUN chmod +x /app/server_thermal_control

# 切换到应用用户
USER thermal

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV RUST_LOG=info
ENV CONFIG_PATH=/app/config/app.toml

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# 启动应用程序
CMD ["/app/server_thermal_control"]