#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
简单的Firefox测试脚本
"""
import os
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def test_environment():
    """测试环境设置"""
    print("=== 环境测试 ===")
    
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
    
    # 测试显示（使用更简单的方法）
    try:
        # 尝试使用xrandr测试显示
        result = subprocess.run(['xrandr', '-display', display], 
                               capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ 显示环境正常")
        else:
            # 如果xrandr失败，尝试其他方法
            print("⚠️  xrandr测试失败，尝试其他方法...")
            # 检查Xvfb进程是否在监听端口
            result = subprocess.run(['netstat', '-tlnp'], 
                                   capture_output=True, text=True)
            if ':99' in result.stdout or 'Xvfb' in result.stdout:
                print("✅ 显示环境正常（通过进程检查）")
            else:
                print("❌ 显示环境异常")
                return False
    except Exception as e:
        print("⚠️  显示测试失败: {}，但继续测试Firefox".format(e))
        # 不返回False，继续测试Firefox
    
    return True

def test_firefox():
    """测试Firefox启动"""
    print("\n=== Firefox测试 ===")
    
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        print("正在启动Firefox...")
        browser = webdriver.Firefox(options=options)
        print("✅ Firefox启动成功!")
        
        # 测试访问网页
        print("正在测试网页访问...")
        browser.get("https://www.baidu.com")
        print("✅ 网页访问成功!")
        
        browser.quit()
        print("✅ Firefox已关闭")
        return True
        
    except Exception as e:
        print("❌ Firefox测试失败: {}".format(e))
        return False

def main():
    print("=== Ubuntu Firefox 环境测试 ===")
    
    # 测试环境
    if not test_environment():
        print("\n❌ 环境测试失败，请先设置虚拟显示环境")
        return False
    
    # 测试Firefox
    if not test_firefox():
        print("\n❌ Firefox测试失败")
        return False
    
    print("\n🎉 所有测试通过！可以运行爬虫程序")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
