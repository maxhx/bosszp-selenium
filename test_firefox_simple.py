#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
简化的Firefox测试脚本
"""
import os
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def check_basic_env():
    """检查基本环境"""
    print("=== 基本环境检查 ===")
    
    # 检查DISPLAY
    display = os.environ.get('DISPLAY')
    print("DISPLAY环境变量: {}".format(display))
    
    if not display:
        print("❌ DISPLAY未设置")
        print("请运行: export DISPLAY=:99")
        return False
    
    # 检查Xvfb进程
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'Xvfb' in result.stdout:
            print("✅ 找到Xvfb进程")
        else:
            print("❌ 未找到Xvfb进程")
            print("请运行: Xvfb :99 -screen 0 1024x768x24 &")
            return False
    except:
        print("⚠️  无法检查Xvfb进程")
    
    return True

def test_firefox_simple():
    """简单测试Firefox"""
    print("\n=== Firefox简单测试 ===")
    
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        
        print("正在启动Firefox...")
        browser = webdriver.Firefox(options=options)
        print("✅ Firefox启动成功!")
        
        browser.quit()
        print("✅ Firefox已关闭")
        return True
        
    except Exception as e:
        print("❌ Firefox测试失败: {}".format(e))
        return False

def main():
    print("=== Ubuntu Firefox 简化测试 ===")
    
    # 检查基本环境
    if not check_basic_env():
        print("\n❌ 基本环境检查失败")
        return False
    
    # 测试Firefox
    if not test_firefox_simple():
        print("\n❌ Firefox测试失败")
        return False
    
    print("\n🎉 测试通过！可以运行爬虫程序")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
