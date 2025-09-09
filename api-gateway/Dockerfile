# API Gateway Dockerfile
# 智能运维平台API网关服务
# 基于Node.js Express框架

FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./

# 安装依赖
RUN npm install --production

# 复制应用代码
COPY . .

# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S apigateway -u 1001

# 更改文件所有权
RUN chown -R apigateway:nodejs /app
USER apigateway

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 启动应用
CMD ["node", "index.js"]