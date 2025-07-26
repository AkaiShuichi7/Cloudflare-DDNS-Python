import os
import platform
import requests
import tarfile
import subprocess
import csv
import shutil
from . import config

# CloudflareST GitHub 仓库信息
CFST_REPO = "XIU2/CloudflareSpeedTest"
CFST_API_URL = f"https://api.github.com/repos/{CFST_REPO}/releases/latest"

# 目标目录
# 将所有临时文件和结果都放在 /app 目录下，方便 Docker 卷挂载
APP_DIR = "/app"
EXECUTABLE_NAME = "cfst"
RESULT_FILE = os.path.join(APP_DIR, "result.csv")
EXECUTABLE_PATH = os.path.join(APP_DIR, EXECUTABLE_NAME)


def get_arch():
    """获取系统架构"""
    arch = platform.machine().lower()
    if "aarch64" in arch or "arm64" in arch:
        return "arm64"
    elif "x86_64" in arch or "amd64" in arch:
        return "amd64"
    else:
        raise OSError(f"不支持的系统架构: {arch}")


def get_download_url():
    """从 GitHub API 获取最新版本的 CloudflareST 下载地址"""
    try:
        response = requests.get(CFST_API_URL)
        response.raise_for_status()
        assets = response.json().get("assets", [])
        arch = get_arch()
        # 根据用户反馈和实际发布的文件名格式 (e.g., CloudflareST_linux_amd64.tar.gz), 关键词应为 linux_amd64
        keyword = f"linux_{arch}"

        for asset in assets:
            # 同时检查文件名是否以 .tar.gz 结尾
            asset_name = asset.get("name", "").lower()
            if keyword in asset_name and asset_name.endswith(".tar.gz"):
                return asset.get("browser_download_url")

        raise FileNotFoundError(f"未能在最新版本中找到适用于 {keyword} 的文件。")
    except requests.RequestException as e:
        print(f"错误: 获取下载地址失败: {e}")
        return None


def setup_speedtest_tool():
    """下载并解压 CloudflareST 工具"""
    if os.path.exists(EXECUTABLE_PATH):
        print(f"测速工具 {EXECUTABLE_PATH} 已存在，跳过下载。")
        return True

    download_url = get_download_url()
    if not download_url:
        return False

    print(f"正在从 {download_url} 下载测速工具...")

    try:
        # 确保 /app 目录存在
        os.makedirs(APP_DIR, exist_ok=True)

        archive_path = os.path.join(APP_DIR, "cfst.tar.gz")

        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(archive_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print("下载完成，正在解压...")
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            # 解压所有文件到目标目录，不保留原始目录结构
            for member in tar_ref.getmembers():
                # 只提取文件，并去除路径，直接放在 APP_DIR 下
                if member.isfile():
                    member.name = os.path.basename(member.name)
                    tar_ref.extract(member, path=APP_DIR)

        # 添加可执行权限
        os.chmod(EXECUTABLE_PATH, 0o755)

        # 清理压缩文件
        os.remove(archive_path)

        print(f"测速工具已成功解压到 {APP_DIR}")
        return True

    except (requests.RequestException, tarfile.TarError, OSError) as e:
        print(f"错误: 准备测速工具时出错: {e}")
        return False


def run_speedtest():
    """执行 CloudflareST 测速"""
    if not setup_speedtest_tool():
        return None

    # 根据 IP 版本选择对应的 IP 文件名
    # IPv4 对应 ip.txt, IPv6 对应 ipv6.txt
    ip_file_name = "ip.txt" if config.IP_VERSION == "ipv4" else "ipv6.txt"
    ip_file_path = os.path.join(APP_DIR, ip_file_name)

    # 构建命令行参数
    cmd = [
        EXECUTABLE_PATH,
        "-f",
        ip_file_path,
        "-o",
        RESULT_FILE,
        "-p",
        config.CFST_DOWNLOAD_COUNT,
        "-n",
        config.CFST_THREADS,
        "-t",
        config.CFST_TEST_COUNT,
        "-sl",
        config.CFST_MIN_DOWNLOAD_SPEED,
        "-tl",
        config.CFST_MAX_LATENCY,
        "-tll",
        config.CFST_MIN_LATENCY,
        "-tlr",
        config.CFST_MAX_PACKET_LOSS,
        "-dt",
        config.CFST_DOWNLOAD_TIMEOUT,
        "-tp",
        config.CFST_PORT,
    ]
    if config.CFST_URL:
        cmd.extend(["-url", config.CFST_URL])

    print(f"正在执行测速命令: {' '.join(cmd)}")

    try:
        # 清理旧的 result.csv
        if os.path.exists(RESULT_FILE):
            os.remove(RESULT_FILE)

        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("测速完成。")
        print("测速工具输出:\n", process.stdout)
        return get_best_ip()
    except subprocess.CalledProcessError as e:
        print(f"错误: 测速失败。返回码: {e.returncode}")
        print("错误输出:\n", e.stderr)
        return None
    except FileNotFoundError:
        print(f"错误: 找不到测速结果文件 {RESULT_FILE}")
        return None


def get_top_ips(count=1):
    """从 result.csv 文件中获取指定数量的优质 IP 列表"""
    ips = []
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # 跳过表头
            next(reader, None)
            # 读取最多 count 个 IP
            for i, row in enumerate(reader):
                if i >= count:
                    break
                if row and len(row) > 0:
                    ips.append(row)  # IP 地址是第一列
        
        if not ips:
            print("警告: result.csv 文件中未找到任何有效的 IP 地址。")
        
        return ips
    except (FileNotFoundError, StopIteration):
        print(f"错误: 测速结果文件 {RESULT_FILE} 未找到或为空。")
        return []


def get_best_ip():
    """从 result.csv 文件中获取最优 IP"""
    top_ips = get_top_ips(count=1)
    if top_ips:
        best_ip = top_ips
        print(f"获取到最优 IP: {best_ip}")
        return best_ip
    
    print("警告: 未能从 result.csv 获取到最优 IP。")
    return None


if __name__ == "__main__":
    # 用于测试模块功能
    best_ip_address = run_speedtest()
    if best_ip_address:
        print(f"\n测试完成，最优 IP 是: {best_ip_address}")
    else:
        print("\n测试失败。")
    
    # 测试获取多个 IP
    print("\n测试获取前 5 个 IP...")
    top_5_ips = get_top_ips(5)
    if top_5_ips:
        print("成功获取到前 5 个 IP:")
        for ip in top_5_ips:
            print(ip)
    else:
        print("未能获取到前 5 个 IP。")
