import requests
from . import config

API_BASE_URL = "https://api.cloudflare.com/client/v4"


class CloudflareManager:
    def __init__(self, api_key, email, zone_id):
        if not all([api_key, email, zone_id]):
            raise ValueError("Cloudflare API Key, Email, 和 Zone ID 不能为空。")

        self.headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json",
        }
        self.zone_id = zone_id

    def _request(self, method, endpoint, **kwargs):
        """通用的 API 请求方法"""
        url = f"{API_BASE_URL}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"错误: Cloudflare API 请求失败: {e}")
            if e.response is not None:
                print(f"响应内容: {e.response.text}")
            return None

    def get_dns_record(self, hostname, record_type="A"):
        """根据主机名和记录类型获取 DNS 记录"""
        endpoint = f"/zones/{self.zone_id}/dns_records"
        params = {"name": hostname, "type": record_type}
        data = self._request("GET", endpoint, params=params)

        if data and data.get("success") and data.get("result"):
            # API 可能返回多个记录，通常我们只关心第一个
            return data["result"]

        print(f"未找到主机名 {hostname} 的 {record_type} 记录。")
        return None

    def update_dns_record(self, hostname, ip_address):
        """更新或创建 DNS A 记录"""
        record_type = "A"  # 目前只处理 IPv4
        existing_records = self.get_dns_record(hostname, record_type)

        payload = {
            "type": record_type,
            "name": hostname,
            "content": ip_address,
            "ttl": 60,  # 设置一个较短的 TTL，例如 60 秒
            "proxied": False,  # 通常 DDNS 的 IP 不应被代理
        }

        record_id = None
        if existing_records and len(existing_records) > 0:
            # 如果存在记录，获取第一个记录的 ID
            # API 返回的是一个列表，所以我们取第一个元素（它是一个字典），然后获取其 'id'
            record_id = existing_records[0].get("id")

        if record_id:
            # 更新现有记录
            print(f"正在更新主机名 {hostname} 的 DNS 记录，新 IP 为 {ip_address}...")
            endpoint = f"/zones/{self.zone_id}/dns_records/{record_id}"
            response_data = self._request("PUT", endpoint, json=payload)
        else:
            # 创建新记录
            print(f"正在为主机名 {hostname} 创建新的 DNS 记录，IP 为 {ip_address}...")
            endpoint = f"/zones/{self.zone_id}/dns_records"
            response_data = self._request("POST", endpoint, json=payload)

        if response_data and response_data.get("success"):
            print(f"主机名 {hostname} 的 DNS 记录已成功更新为 {ip_address}。")
            return True
        else:
            print(f"错误: 更新主机名 {hostname} 的 DNS 记录失败。")
            return False


def get_cloudflare_manager():
    """工厂函数，用于创建 CloudflareManager 实例"""
    return CloudflareManager(
        api_key=config.CF_API_KEY, email=config.CF_EMAIL, zone_id=config.CF_ZONE_ID
    )


if __name__ == "__main__":
    # 用于测试模块功能
    try:
        config.validate_config()
        manager = get_cloudflare_manager()

        if config.CF_HOSTNAMES:
            hostname_to_test = config.CF_HOSTNAMES
            print(f"\n正在测试主机名: {hostname_to_test}")

            records = manager.get_dns_record(hostname_to_test)
            if records:
                print(f"找到记录: {records}")
                # 注意：下面的代码会真实地更新你的 DNS 记录
                # manager.update_dns_record(hostname_to_test, "1.2.3.4")
            else:
                print("未找到记录。")
        else:
            print("请在 .env 文件中配置 CF_HOSTNAMES 以进行测试。")

    except ValueError as e:
        print(e)
