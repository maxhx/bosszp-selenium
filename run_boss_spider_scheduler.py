from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import datetime
import sys

def run_boss_spider():
    print(f"{datetime.datetime.now()} 开始执行 boss_selenium_copy.py")
    # 调用 python 运行 boss_selenium_copy.py
    subprocess.run([sys.executable, "boss_selenium_copy.py"])
    print(f"{datetime.datetime.now()} boss_selenium_copy.py 执行完毕")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # 每小时执行一次
    scheduler.add_job(run_boss_spider, 'interval', hours=1)
    # scheduler.add_job(run_boss_spider, 'interval', minutes=5)
    print("定时任务已启动，每1小时执行一次 boss_selenium_copy.py")
    scheduler.start() 