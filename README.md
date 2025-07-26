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

这是最简单、最推荐的部署方式。我们通过 GitHub Actions 自动构建并发布 Docker 镜像到 GitHub Container Registry (GHCR)，您无需在本地构建。

**a. 拉取 Docker 镜像**

从 GHCR 拉取最新的 Docker 镜像：

```bash
docker pull ghcr.io/akaishuichi7/cloudflare-ddns-python:latest
```

**b. 使用 Docker Compose 运行**

我们推荐使用 Docker Compose 进行部署，因为它能更好地管理配置和数据卷。

1.  确保您已经根据 `env.example` 创建并配置好了 `.env` 文件。
2.  在项目根目录下创建一个 `data` 目录，用于持久化测速工具和结果文件。

    ```bash
    mkdir data
    ```
3.  在项目根目录下，执行以下命令启动服务：

    ```bash
    docker-compose up -d
    ```

**c. 手动更新测速工具 (可选)**

在网络不佳的环境下（例如中国大陆），程序可能无法自动从 GitHub 下载测速工具。此时，您可以手动下载并放置。

1.  访问 [CloudflareST 发布页面](https://github.com/XIU2/CloudflareSpeedTest/releases)。
2.  根据您的服务器架构（通常是 `linux_amd64` 或 `linux_arm64`）下载最新的 `.tar.gz` 压缩包。
3.  解压压缩包，找到名为 `CloudflareST` 的可执行文件。
4.  将其重命名为 `cfst`。
5.  将 `cfst` 文件和 `ip.txt` 文件一同放入您在宿主机上创建的 `data` 目录中。
6.  重新启动 Docker 容器 (`docker-compose restart`)，程序会自动使用您提供的工具。

**d. 查看日志**

要查看程序的运行日志，可以使用以下命令：

```bash
docker-compose logs -f
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

## ❤️ 致谢

- 本项目依赖于 [XIU2/CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) 项目提供的强大测速工具，没有它就没有本项目。在此向其开发者 **XIU2** 表示衷心的感谢！
