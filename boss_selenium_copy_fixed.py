#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Ubuntu环境问题修复版本
"""
import datetime
import time
import json
import os
import sys
import signal
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from dbutils import DBUtils
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# 配置环境
ENVIRONMENT = 'production'
DEBUG_MODE = False

def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r') as f:
            configs = json.load(f)
        return configs.get(ENVIRONMENT)
    except FileNotFoundError:
        print("警告: config.json文件未找到")
        return None
    except Exception as e:
        print("警告: 配置文件加载失败: {}".format(e))
        return None

def check_ubuntu_display():
    """检查Ubuntu虚拟显示环境"""
    if not os.path.exists('/etc/os-release'):
        return True  # 不是Ubuntu系统
    
    with open('/etc/os-release', 'r') as f:
        os_info = f.read()
        if 'ubuntu' not in os_info.lower():
            return True  # 不是Ubuntu系统
    
    # 检查DISPLAY环境变量
    display = os.environ.get('DISPLAY')
    if not display:
        print("❌ Ubuntu环境未设置DISPLAY变量")
        print("解决方案:")
        print("1. 安装虚拟显示: apt-get install xvfb")
        print("2. 启动虚拟显示: Xvfb :99 -screen 0 1024x768x24 &")
        print("3. 设置环境变量: export DISPLAY=:99")
        print("4. 或使用: xvfb-run -a python3 boss_selenium_copy.py")
        return False
    
    # 检查Xvfb进程
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'Xvfb' not in result.stdout:
            print("⚠️  未找到Xvfb进程，但DISPLAY已设置")
    except:
        pass
    
    return True

def create_browser_with_timeout():
    """带超时的浏览器创建"""
    print("正在创建Firefox浏览器实例...")
    
    try:
        options = Options()
        
        # Ubuntu服务器环境优化选项
        if not DEBUG_MODE:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        # 重要：不禁用JavaScript，Boss直聘需要JS
        # options.add_argument('--disable-javascript')  # 注释掉这行
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # 尝试不同的Firefox路径
        firefox_paths = [
            "/usr/bin/firefox",
            "/usr/bin/firefox-esr", 
            "/snap/bin/firefox",
            "/opt/firefox/firefox",
            "/usr/local/bin/firefox"
        ]
        
        firefox_found = False
        for path in firefox_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                print("找到可执行的Firefox: {}".format(path))
                options.binary_location = path
                firefox_found = True
                break
        
        if not firefox_found:
            print("警告: 未找到可执行的Firefox浏览器")
        
        # 检查geckodriver
        geckodriver_paths = [
            "/usr/local/bin/geckodriver",
            "/usr/bin/geckodriver",
            "/snap/bin/geckodriver"
        ]
        
        geckodriver_found = False
        for path in geckodriver_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                print("找到可执行的geckodriver: {}".format(path))
                geckodriver_found = True
                break
        
        if not geckodriver_found:
            print("警告: 未找到可执行的geckodriver")
        
        # 检查Ubuntu显示环境
        if not check_ubuntu_display():
            return None
        
        print("正在启动Firefox浏览器...")
        
        # 使用信号实现超时
        def timeout_handler(signum, frame):
            raise TimeoutError("Firefox启动超时（30秒）")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30秒超时
        
        try:
            browser = webdriver.Firefox(options=options)
            signal.alarm(0)  # 取消超时
            print("✅ Firefox浏览器启动成功!")
            return browser
        except TimeoutError:
            signal.alarm(0)
            print("❌ Firefox启动超时")
            print("可能的解决方案:")
            print("1. 使用xvfb-run: xvfb-run -a python3 boss_selenium_copy.py")
            print("2. 手动设置虚拟显示环境")
            return None
        
    except Exception as e:
        print("❌ 创建浏览器失败: {}".format(e))
        print("详细解决方案:")
        print("1. 安装Firefox: apt-get install firefox-esr")
        print("2. 安装geckodriver: wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz")
        print("3. 设置权限: chmod +x /usr/local/bin/geckodriver")
        print("4. 使用xvfb-run: xvfb-run -a python3 boss_selenium_copy.py")
        return None

def main():
    """主函数"""
    print("=== Boss直聘爬虫 Ubuntu修复版 ===")
    
    # 加载配置
    db_config = load_config()
    if not db_config:
        print("无法加载数据库配置，程序退出")
        return
    
    # 创建浏览器实例
    browser = create_browser_with_timeout()
    if not browser:
        print("无法创建浏览器实例，程序退出")
        return
    
    try:
        print("开始爬取数据...")
        # 这里添加你的爬虫逻辑
        browser.get("https://www.baidu.com")
        print("✅ 页面访问成功!")
        
    except Exception as e:
        print("爬虫运行出错: {}".format(e))
    finally:
        if browser:
            browser.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    main()
