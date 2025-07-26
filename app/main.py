import sys
import time
from . import scheduler, config

def main():
    """程序主入口"""
    
    # 检查是否通过命令行参数直接运行任务
    if "--run-task" in sys.argv:
        scheduler.run_update_task()
        return

    print("程序启动...")
    
    # 1. 设置 cron 定时任务
    scheduler.setup_cron_job()

    # 2. 根据配置决定是否立即执行一次任务
    if config.RUN_ON_STARTUP:
        print("\n根据配置，立即执行一次更新任务...")
        scheduler.run_update_task()

    # 3. 对于 Docker 环境，保持程序运行
    #    如果设置了 cron 任务，这里可以让主进程退出或进入休眠
    if config.CRON_SCHEDULE:
        print("\n定时任务已设置。程序将进入休眠状态。")
        print("你可以通过 'cron -l' 查看定时任务。")
        print("要停止此程序，请按 Ctrl+C。")
        try:
            while True:
                time.sleep(3600)  # 每小时唤醒一次，可以根据需要调整
        except KeyboardInterrupt:
            print("\n程序已停止。")
    else:
        print("\n未设置定时任务，程序执行完毕。")

if __name__ == "__main__":
    main()
