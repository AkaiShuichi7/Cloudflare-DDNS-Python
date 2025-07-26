# 使用官方 Python slim 镜像作为基础
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装 cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 创建并设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 使用 pip 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY app/ ./app/

# 创建并声明数据卷，用于持久化测速工具和结果
RUN mkdir /data
VOLUME /data

# 复制 .env.example，在实际运行时应通过卷挂载 .env 文件
COPY .env.example ./.env

# 使用 JSON 格式以避免信号处理问题
CMD ["sh", "-c", "service cron start && python -m app.main"]
