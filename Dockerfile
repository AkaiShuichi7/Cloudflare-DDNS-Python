# ---- Builder Stage ----
# 使用一个包含完整构建工具的镜像作为构建环境
FROM python:3.10 as builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装 poetry
RUN pip install poetry

# 设置工作目录
WORKDIR /app

# 复制项目依赖定义文件
COPY pyproject.toml poetry.lock ./

# 使用 poetry 生成 requirements.txt 并安装依赖到指定目录
# 这样做可以缓存依赖层，并且最终镜像中不需要 poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    poetry export -f requirements.txt --output requirements.txt --without-hashes

# ---- Final Stage ----
# 使用一个轻量的 slim 镜像作为最终的运行环境
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装 cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 创建并设置工作目录
WORKDIR /app

# 从 builder 阶段复制已安装的依赖
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/requirements.txt .

# 复制应用程序代码
COPY app/ ./app/

# 复制 .env.example，在实际运行时应通过卷挂载 .env 文件
COPY .env.example ./.env

# 使用 JSON 格式以避免信号处理问题
CMD ["sh", "-c", "service cron start && python -m app.main"]
