#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
服务器环境诊断脚本
"""
import os
import subprocess
import sys

def check_firefox():
    """检查Firefox安装"""
    print("=== 检查Firefox浏览器 ===")
    
    firefox_paths = [
        "/usr/bin/firefox",
        "/usr/bin/firefox-esr", 
        "/snap/bin/firefox",
        "/opt/firefox/firefox",
        "/usr/local/bin/firefox"
    ]
    
    firefox_found = False
    for path in firefox_paths:
        if os.path.exists(path):
            print("✅ 找到Firefox: {}".format(path))
            try:
                result = subprocess.run([path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("   版本: {}".format(result.stdout.strip()))
                else:
                    print("   版本检查失败")
            except Exception as e:
                print("   版本检查出错: {}".format(e))
            firefox_found = True
            break
    
    if not firefox_found:
        print("❌ 未找到Firefox浏览器")
        print("安装命令: apt-get install firefox-esr")
        return False
    
    return True

def check_geckodriver():
    """检查geckodriver"""
    print("\n=== 检查geckodriver ===")
    
    geckodriver_paths = [
        "/usr/local/bin/geckodriver",
        "/usr/bin/geckodriver",
        "/snap/bin/geckodriver"
    ]
    
    geckodriver_found = False
    for path in geckodriver_paths:
        if os.path.exists(path):
            print("✅ 找到geckodriver: {}".format(path))
            try:
                result = subprocess.run([path, "--version"], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("   版本: {}".format(result.stdout.strip()))
                else:
                    print("   版本检查失败")
            except Exception as e:
                print("   版本检查出错: {}".format(e))
            geckodriver_found = True
            break
    
    if not geckodriver_found:
        print("❌ 未找到geckodriver")
        print("安装命令:")
        print("wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz")
        print("tar -xzf geckodriver-v0.33.0-linux64.tar.gz")
        print("sudo mv geckodriver /usr/local/bin/")
        print("sudo chmod +x /usr/local/bin/geckodriver")
        return False
    
    return True

def check_display():
    """检查显示环境"""
    print("\n=== 检查显示环境 ===")
    
    display = os.environ.get('DISPLAY')
    if display:
        print("✅ DISPLAY环境变量: {}".format(display))
    else:
        print("⚠️  未设置DISPLAY环境变量 (无头模式需要)")
    
    # 检查Xvfb
    try:
        result = subprocess.run(['which', 'Xvfb'], 
                             capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 找到Xvfb虚拟显示")
        else:
            print("⚠️  未找到Xvfb (可选)")
    except:
        print("⚠️  无法检查Xvfb")

def check_selenium():
    """检查Selenium"""
    print("\n=== 检查Selenium ===")
    
    try:
        import selenium
        print("✅ Selenium已安装: {}".format(selenium.__version__))
        
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        print("✅ Firefox WebDriver可用")
        
    except ImportError as e:
        print("❌ Selenium导入失败: {}".format(e))
        return False
    
    return True

def test_browser_creation():
    """测试浏览器创建"""
    print("\n=== 测试浏览器创建 ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        print("正在尝试创建Firefox浏览器...")
        browser = webdriver.Firefox(options=options)
        print("✅ Firefox浏览器创建成功!")
        
        browser.quit()
        print("✅ 浏览器已正确关闭")
        return True
        
    except Exception as e:
        print("❌ 浏览器创建失败: {}".format(e))
        return False

def main():
    print("=== Boss直聘爬虫服务器环境诊断 ===\n")
    
    checks = [
        ("Firefox浏览器", check_firefox),
        ("geckodriver", check_geckodriver),
        ("显示环境", check_display),
        ("Selenium", check_selenium),
        ("浏览器创建", test_browser_creation)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print("检查{}时出错: {}".format(name, e))
            results.append((name, False))
    
    print("\n=== 诊断结果 ===")
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print("{}: {}".format(name, status))
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查通过！可以运行爬虫程序")
    else:
        print("\n⚠️  部分检查失败，请解决上述问题后重试")

if __name__ == "__main__":
    main()
