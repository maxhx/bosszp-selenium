#!/bin/bash

# Ubuntu虚拟显示环境一键设置

echo "=== Ubuntu虚拟显示环境一键设置 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行: sudo $0"
    exit 1
fi

# 安装xvfb
echo "1. 安装xvfb..."
apt-get update
apt-get install -y xvfb

# 杀死现有Xvfb进程
echo "2. 清理现有进程..."
pkill -f Xvfb 2>/dev/null || true
sleep 1

# 启动虚拟显示
echo "3. 启动虚拟显示..."
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2

# 检查是否启动成功
if ps -p $XVFB_PID > /dev/null; then
    echo "✅ 虚拟显示启动成功 (PID: $XVFB_PID)"
else
    echo "❌ 虚拟显示启动失败"
    exit 1
fi

# 设置环境变量
export DISPLAY=:99
echo "✅ 设置DISPLAY=:99"

# 测试虚拟显示
echo "4. 测试虚拟显示..."
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ 虚拟显示测试通过"
else
    echo "❌ 虚拟显示测试失败"
    exit 1
fi

echo ""
echo "🎉 设置完成！现在可以运行:"
echo "python3 boss_selenium_copy.py"
echo ""
echo "注意: 如果关闭终端，需要重新运行此脚本"
