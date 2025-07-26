import sys
import os
from crontab import CronTab
from . import config, speedtest, cloudflare


def run_update_task():
    """执行一次完整的测速和 DNS 更新任务"""
    print("=" * 30)
    print("开始执行 DDNS 更新任务...")

    try:
        # 1. 验证配置
        config.validate_config()

        num_hostnames = len(config.CF_HOSTNAMES)
        if num_hostnames == 0:
            print("未配置任何域名 (CF_HOSTNAMES)，任务终止。")
            return

        # 2. 执行测速并获取相应数量的 IP
        # 注意: 此处假设测速已完成，直接从结果文件获取 IP。
        # 在实际运行中，您可能需要取消下面这行代码的注释。
        # speedtest.run_speedtest()

        print(f"需要为 {num_hostnames} 个域名获取 {num_hostnames} 个最优 IP...")
        top_ip_infos = speedtest.get_top_ips(count=num_hostnames)

        if not top_ip_infos or len(top_ip_infos) < num_hostnames:
            print(
                f"错误: 需要 {num_hostnames} 个 IP，但只获取到 {len(top_ip_infos)} 个。任务终止。"
            )
            print("请检查测速工具是否能产生足够数量的有效 IP。")
            return

        print(f"成功获取到 {len(top_ip_infos)} 个优质 IP。")

        # 3. 更新 DNS 记录
        cf_manager = cloudflare.get_cloudflare_manager()
        success_count = 0

        # 将域名和 IP 地址一一对应进行更新
        for hostname, ip_info in zip(config.CF_HOSTNAMES, top_ip_infos):
            ip_address = ip_info[0]  # 从列表中提取 IP 地址（第一列）
            print(f"\n> 正在更新域名: {hostname} -> 新 IP: {ip_address}")
            if cf_manager.update_dns_record(hostname, ip_address):
                success_count += 1

        print(f"\n任务完成: {success_count} / {num_hostnames} 个域名已成功更新。")

    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"执行任务时发生未知错误: {e}")
    finally:
        print("=" * 30)


def setup_cron_job():
    """根据配置设置或移除 cron 任务"""
    if not config.CRON_SCHEDULE:
        print("未配置 CRON_SCHEDULE，跳过定时任务设置。")
        return

    try:
        # 使用当前用户的 crontab
        cron = CronTab(user=True)

        # 任务的唯一标识
        comment = "cfstddns_auto_update"

        # 移除旧的同名任务
        cron.remove_all(comment=comment)

        # 创建新任务
        # 获取当前 Python 解释器的路径
        python_executable = sys.executable
        # 获取主脚本的绝对路径
        main_script_path = os.path.join(config.BASE_DIR, "app", "main.py")

        command = f"{python_executable} {main_script_path} --run-task"

        job = cron.new(command=command, comment=comment)

        if job.is_valid():
            job.setall(config.CRON_SCHEDULE)
            cron.write()
            print(f"已成功设置 cron 任务，表达式为: '{config.CRON_SCHEDULE}'")
            print(f"执行的命令为: {command}")
        else:
            print(f"错误: 无效的 cron 表达式: '{config.CRON_SCHEDULE}'")

    except Exception as e:
        print(f"错误: 设置 cron 任务失败: {e}")
        print("请确保您有权限操作 crontab，并且 'cron' 服务正在运行。")


if __name__ == "__main__":
    # 用于测试模块功能
    print("测试执行一次更新任务...")
    run_update_task()

    print("\n测试设置 cron 任务...")
    setup_cron_job()
