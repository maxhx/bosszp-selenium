#!/bin/bash

# 使用xvfb-run启动爬虫

echo "=== 使用xvfb-run启动Boss爬虫 ==="

# 检查xvfb-run是否可用
if ! command -v xvfb-run &> /dev/null; then
    echo "❌ xvfb-run未安装"
    echo "正在安装..."
    apt-get update
    apt-get install -y xvfb
fi

echo "✅ xvfb-run已就绪"

# 使用xvfb-run启动爬虫
echo "正在启动爬虫..."
xvfb-run -a python3 boss_selenium_copy.py

echo "爬虫执行完成"
