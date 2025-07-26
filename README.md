# cfstddns - Python 版

这是一个使用 Python 重新实现的 `CloudflareSpeedTestDDNS` 工具，旨在通过优选 Cloudflare IP 并自动更新 DNS 记录来优化网络连接。

## ✨ 功能特性

- **纯 Python 实现**: 核心逻辑完全使用 Python 编写，移除了复杂的 shell 脚本。
- **动态 IP 优选**: 自动下载并运行最新的 `CloudflareST` 工具，以获取当前网络环境下最优的 Cloudflare IP。
- **自动 DDNS**: 将最优 IP 自动更新到您在 Cloudflare 上配置的多个域名。
- **灵活的定时任务**: 使用 `cron` 进行任务调度，您可以自定义任务执行的频率。
- **环境变量配置**: 所有配置均通过 `.env` 文件管理，清晰、安全且易于在 Docker 环境中使用。
- **Docker 化**: 提供 `Dockerfile`，支持一键构建和部署。
- **启动时执行**: 可配置在程序启动时立即执行一次更新任务，方便快速验证。

## 🚀 快速开始

### 1. 配置

首先，将项目根目录下的 `.env.example` 文件复制一份并重命名为 `.env`。

```bash
cp .env.example .env
```

然后，使用文本编辑器打开 `.env` 文件，并根据文件内的注释填写您的配置信息，特别是以下几项：

- `CRON_SCHEDULE`: 定时任务的执行周期。
- `CF_API_KEY`: 你的 Cloudflare Global API Key。
- `CF_EMAIL`: 你的 Cloudflare 登录邮箱。
- `CF_ZONE_ID`: 你的域名所在的区域 ID。
- `CF_HOSTNAMES`: 需要更新的域名列表，用空格隔开。

### 2. 使用 Docker 部署 (推荐)

这是最简单、最推荐的部署方式。

**a. 构建 Docker 镜像**

在项目根目录下，执行以下命令来构建镜像：

```bash
docker build -t cfstddns-py .
```

**b. 运行 Docker 容器**

使用以下命令在后台运行容器。请确保您已经创建并配置好了 `.env` 文件。

```bash
docker run -d \
  --name my-cfstddns \
  --restart always \
  -v $(pwd)/.env:/app/.env \
  cfstddns-py
```

- `-d`: 后台运行容器。
- `--name`: 为容器指定一个名称。
- `--restart always`: 确保容器在退出或服务器重启后能自动重启。
- `-v $(pwd)/.env:/app/.env`: 将您本地的 `.env` 文件挂载到容器内部，这是**必须**的步骤，以便程序能读取到您的配置。

**c. 查看日志**

要查看程序的运行日志，可以使用以下命令：

```bash
docker logs -f my-cfstddns
```

### 3. 本地运行与测试 (适用于开发)

如果您想在本地直接运行和测试，请确保您的系统已经安装了 Python 3.8+ 和 `poetry`。

**a. 安装 Poetry**

如果您尚未安装 `poetry`，请参考其[官方文档](https://python-poetry.org/docs/#installation)进行安装。

**b. 安装依赖**

在项目根目录下，执行以下命令来安装所有 Python 依赖：

```bash
poetry install
```

**c. 运行程序**

配置好 `.env` 文件后，通过 `poetry` 运行主程序：

```bash
poetry run python -m app.main
```

程序将根据您的配置设置 `cron` 任务，并可能在启动时执行一次。

**d. 直接执行一次性任务**

如果您只想手动触发一次测速和更新任务，而不设置 `cron` 或作为服务运行，可以使用 `--run-task` 参数：

```bash
poetry run python -m app.main --run-task
```

## ⚙️ 配置项说明

所有配置项都在 `.env` 文件中，详细说明请参考文件内的注释。

## 🤝 贡献

欢迎提交 Pull Request 或提出 Issues 来改进这个项目。
