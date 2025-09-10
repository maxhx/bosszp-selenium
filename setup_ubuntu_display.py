#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Ubuntu虚拟显示环境设置脚本
"""
import os
import subprocess
import sys

def check_xvfb():
    """检查xvfb是否已安装"""
    try:
        result = subprocess.run(['which', 'xvfb-run'], 
                               capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_xvfb():
    """安装xvfb"""
    print("正在安装xvfb...")
    try:
        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'xvfb'], check=True)
        print("✅ xvfb安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ xvfb安装失败: {}".format(e))
        return False

def start_virtual_display():
    """启动虚拟显示"""
    print("正在启动虚拟显示...")
    try:
        # 杀死现有进程
        subprocess.run(['pkill', '-f', 'Xvfb'], 
                      capture_output=True)
        
        # 启动新的虚拟显示
        cmd = ['Xvfb', ':99', '-screen', '0', '1024x768x24', 
               '-ac', '+extension', 'GLX', '+render', '-noreset']
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL)
        
        # 等待启动
        import time
        time.sleep(2)
        
        # 检查是否启动成功
        result = subprocess.run(['xdpyinfo', '-display', ':99'], 
                               capture_output=True)
        if result.returncode == 0:
            print("✅ 虚拟显示启动成功")
            return True
        else:
            print("❌ 虚拟显示启动失败")
            return False
    except Exception as e:
        print("❌ 启动虚拟显示时出错: {}".format(e))
        return False

def set_display_env():
    """设置DISPLAY环境变量"""
    os.environ['DISPLAY'] = ':99'
    print("✅ 设置DISPLAY=:99")

def main():
    print("=== Ubuntu虚拟显示环境设置 ===")
    
    # 检查是否为Ubuntu
    if not os.path.exists('/etc/os-release'):
        print("❌ 不是Ubuntu系统")
        return False
    
    with open('/etc/os-release', 'r') as f:
        os_info = f.read()
        if 'ubuntu' not in os_info.lower():
            print("❌ 不是Ubuntu系统")
            return False
    
    print("✅ 检测到Ubuntu系统")
    
    # 检查并安装xvfb
    if not check_xvfb():
        print("xvfb未安装，正在安装...")
        if not install_xvfb():
            return False
    else:
        print("✅ xvfb已安装")
    
    # 启动虚拟显示
    if not start_virtual_display():
        return False
    
    # 设置环境变量
    set_display_env()
    
    print("\n🎉 虚拟显示环境设置完成！")
    print("现在可以运行爬虫程序:")
    print("python3 boss_selenium_copy.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
