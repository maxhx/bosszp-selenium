#!/bin/bash

# Ubuntu服务器环境启动脚本

echo "=== Boss直聘爬虫 Ubuntu启动脚本 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本"
    exit 1
fi

# 安装必要的依赖
echo "1. 安装虚拟显示环境..."
apt-get update
apt-get install -y xvfb

# 启动虚拟显示
echo "2. 启动虚拟显示环境..."
# 杀死可能存在的Xvfb进程
pkill -f Xvfb 2>/dev/null || true
sleep 1

# 启动新的Xvfb进程
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

# 等待Xvfb启动
sleep 3

# 检查Xvfb是否启动成功
if ps -p $XVFB_PID > /dev/null; then
    echo "✅ 虚拟显示环境启动成功 (PID: $XVFB_PID)"
else
    echo "❌ 虚拟显示环境启动失败"
    exit 1
fi

# 设置显示环境变量
export DISPLAY=:99
echo "✅ 设置DISPLAY=:99"

# 测试虚拟显示
echo "3. 测试虚拟显示环境..."
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ 虚拟显示环境测试通过"
else
    echo "❌ 虚拟显示环境测试失败"
    exit 1
fi

# 切换到项目目录
cd /root/app/bosszp-selenium-master

# 运行诊断
echo "4. 运行环境诊断..."
python3 diagnose_server.py

# 测试浏览器创建
echo "5. 测试浏览器创建..."
python3 boss_selenium_copy.py test

if [ $? -eq 0 ]; then
    echo "6. 启动爬虫程序..."
    python3 boss_selenium_copy.py
else
    echo "❌ 浏览器测试失败，请检查环境配置"
fi

# 清理函数
cleanup() {
    echo "清理虚拟显示环境..."
    kill $XVFB_PID 2>/dev/null || true
    pkill -f Xvfb 2>/dev/null || true
}

# 设置退出时清理
trap cleanup EXIT

echo "脚本执行完成"
