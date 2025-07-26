# 使用官方 Python 镜像作为基础
FROM python:3.10-slim

# 设置环境变量，防止 Python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装 cron 和 poetry
RUN apt-get update && \
    apt-get install -y cron && \
    pip install poetry

# 创建并设置工作目录
WORKDIR /app

# 复制项目定义文件
COPY pyproject.toml poetry.lock* ./

# 安装项目依赖，不创建虚拟环境
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# 复制应用程序代码和配置文件
COPY app/ ./app/
COPY .env.example ./.env

# 暴露端口（如果需要的话，这里只是示例）
# EXPOSE 80

# 定义容器启动时执行的命令
# 启动 cron 服务并在前台运行我们的 Python 应用
CMD service cron start && python -m app.main
