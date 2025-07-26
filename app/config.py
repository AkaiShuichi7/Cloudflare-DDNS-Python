import os
from dotenv import load_dotenv

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载 .env 文件
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # 在 Docker 或其他环境中，可能直接设置了环境变量
    print("警告: .env 文件未找到。将依赖于系统环境变量。")

def get_env_variable(var_name, default=None):
    """获取环境变量，如果未设置则返回默认值。"""
    return os.environ.get(var_name, default)

def get_bool_env_variable(var_name, default=False):
    """获取布尔类型的环境变量。"""
    value = get_env_variable(var_name, str(default)).lower()
    return value in ['true', '1', 't', 'y', 'yes']

# --- 任务调度配置 ---
CRON_SCHEDULE = get_env_variable("CRON_SCHEDULE")
RUN_ON_STARTUP = get_bool_env_variable("RUN_ON_STARTUP", True)

# --- Cloudflare API 配置 ---
CF_API_KEY = get_env_variable("CF_API_KEY")
CF_EMAIL = get_env_variable("CF_EMAIL")
CF_ZONE_ID = get_env_variable("CF_ZONE_ID")

# --- DDNS 配置 ---
# 将空格分隔的域名字符串转换为列表
hostnames_str = get_env_variable("CF_HOSTNAMES", "")
CF_HOSTNAMES = hostnames_str.split() if hostnames_str else []

# --- CloudflareST 测速工具配置 ---
IP_VERSION = get_env_variable("IP_VERSION", "ipv4")
CFST_URL = get_env_variable("CFST_URL")
CFST_PORT = get_env_variable("CFST_PORT", "443")
CFST_DOWNLOAD_TIMEOUT = get_env_variable("CFST_DOWNLOAD_TIMEOUT", "10")
CFST_THREADS = get_env_variable("CFST_THREADS", "200")
CFST_TEST_COUNT = get_env_variable("CFST_TEST_COUNT", "4")
CFST_DOWNLOAD_COUNT = get_env_variable("CFST_DOWNLOAD_COUNT", "10")
CFST_MAX_LATENCY = get_env_variable("CFST_MAX_LATENCY", "9999")
CFST_MIN_LATENCY = get_env_variable("CFST_MIN_LATENCY", "0")
CFST_MAX_PACKET_LOSS = get_env_variable("CFST_MAX_PACKET_LOSS", "1.00")
CFST_MIN_DOWNLOAD_SPEED = get_env_variable("CFST_MIN_DOWNLOAD_SPEED", "0.00")

def validate_config():
    """验证关键配置是否已设置。"""
    required_vars = {
        "CF_API_KEY": CF_API_KEY,
        "CF_EMAIL": CF_EMAIL,
        "CF_ZONE_ID": CF_ZONE_ID,
        "CF_HOSTNAMES": CF_HOSTNAMES
    }
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"错误: 缺少以下必要的环境变量: {', '.join(missing_vars)}")
    print("配置加载成功并通过验证。")

if __name__ == '__main__':
    # 用于测试配置加载
    try:
        validate_config()
        print("\n所有配置项:")
        for key, value in globals().items():
            if key.isupper():
                print(f"{key}: {value}")
    except ValueError as e:
        print(e)
