#!/bin/bash

# Ubuntu快速修复脚本

echo "=== Ubuntu Firefox 快速修复 ==="

# 安装xvfb
echo "安装虚拟显示环境..."
apt-get update
apt-get install -y xvfb

# 杀死现有进程
echo "清理现有进程..."
pkill -f Xvfb 2>/dev/null || true
sleep 1

# 启动虚拟显示
echo "启动虚拟显示..."
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
sleep 2

# 设置环境变量
export DISPLAY=:99
echo "设置 DISPLAY=:99"

# 测试显示
echo "测试虚拟显示..."
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ 虚拟显示正常"
else
    echo "❌ 虚拟显示异常"
    exit 1
fi

echo "修复完成！现在可以运行:"
echo "python3 boss_selenium_copy.py"
