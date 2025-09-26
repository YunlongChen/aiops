# 多阶段构建Dockerfile for 服务器热控制系统

# 构建阶段 - 使用本地基础镜像# 构建阶段
FROM thermal-control-base:latest AS builder

# 安装Rust工具链和构建工具
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 配置Cargo使用国内镜像源
RUN mkdir -p /root/.cargo && \
    echo '[source.crates-io]' > /root/.cargo/config.toml && \
    echo 'replace-with = "rsproxy-sparse"' >> /root/.cargo/config.toml && \
    echo '[source.rsproxy-sparse]' >> /root/.cargo/config.toml && \
    echo 'registry = "sparse+https://rsproxy.cn/index/"' >> /root/.cargo/config.toml

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制源代码
COPY Cargo.toml ./
COPY src ./src

# 构建应用
RUN cargo build --release

# 运行时阶段
FROM thermal-control-base:latest AS runtime

# 复制构建产物
COPY --from=builder /app/target/release/server_thermal_control ./

# 创建数据目录
RUN mkdir -p data logs

# 设置权限
RUN chown -R thermal:thermal /app

# 切换到应用用户
USER thermal

# 暴露端口
EXPOSE 8080

# 启动应用
CMD ["./server_thermal_control"]