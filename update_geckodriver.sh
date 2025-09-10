#!/bin/bash

# geckodriver更新脚本

echo "=== 更新geckodriver到最新版本 ==="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行: sudo $0"
    exit 1
fi

# 下载最新版本的geckodriver
echo "1. 下载geckodriver v0.36.0..."
cd /tmp
wget -O geckodriver-v0.36.0-linux64.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ 下载失败"
    exit 1
fi

echo "✅ 下载完成"

# 解压
echo "2. 解压geckodriver..."
tar -xzf geckodriver-v0.33.0-linux64.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ 解压失败"
    exit 1
fi

echo "✅ 解压完成"

# 移动到系统路径
echo "3. 安装geckodriver..."
mv geckodriver /usr/local/bin/
chmod +x /usr/local/bin/geckodriver

if [ $? -ne 0 ]; then
    echo "❌ 安装失败"
    exit 1
fi

echo "✅ 安装完成"

# 验证安装
echo "4. 验证安装..."
geckodriver --version

if [ $? -eq 0 ]; then
    echo "✅ geckodriver安装成功"
else
    echo "❌ geckodriver安装失败"
    exit 1
fi

# 清理临时文件
rm -f geckodriver-v0.33.0-linux64.tar.gz

echo ""
echo "🎉 geckodriver更新完成！"
echo "现在可以运行: xvfb-run -a python3 boss_selenium_copy.py test"
