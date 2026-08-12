# ============================================================
# 阶段一：构建阶段 - 安装依赖 builder
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装依赖（利用 Docker 缓存层，依赖不变时跳过安装）
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# 阶段二：运行阶段 - 最小化镜像
# ============================================================
FROM python:3.11-slim AS runtime

# 环境变量：默认端口 8080，可通过 -e PORT=xxxx 覆盖
ENV PORT=8080

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /sbin/nologin appuser

WORKDIR /app

# 从构建阶段复制已安装的依赖
COPY --from=builder /install /usr/local

# 复制应用源码
COPY src/ ./src/

# 切换到非 root 用户
USER appuser

# 暴露端口（由环境变量 PORT 控制）
EXPOSE ${PORT}

# 启动命令（生产模式，无 reload）
CMD ["sh", "-c", "cd src && python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
